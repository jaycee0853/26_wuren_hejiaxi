import torch
from torch import nn
from torchvision import transforms,datasets
from torch.utils.data.dataloader import DataLoader
import torch.optim as optim
import torch.nn.functional as F
from torchinfo import summary
import os

class mixed_net(nn.Module):
    """
    自己写的CNN网络，用来分类锥桶图片（blue、red、yellow三种）

    一共5层：3个卷积层 + 2个全连接层
    不算激活函数和Dropout的话不超过10层，全连接也不超过3层，符合作业要求

    我参考了PPT里的CNN结构，大概就是 卷积→激活→池化 这样叠几层，
    然后展平接全连接层输出分类结果
    """

    def __init__(self):
        super(mixed_net,self).__init__()

        # ---- 卷积层 ----

        # conv1: 输入(3, 64, 64) -> 输出(32, 64, 64)
        # 3是RGB三个通道，32是输出通道数（就是卷积核的数量）
        # kernel_size=3就是3x3的卷积核，padding=1是为了让卷积后尺寸不变
        # 尺寸计算公式PPT里有：W_out = (W_in + 2*padding - kernel_size) / stride + 1
        #                      = (64 + 2*1 - 3) / 1 + 1 = 64  没毛病
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1)

        # conv2: 输入(32, 32, 32) -> 输出(64, 32, 32)
        # 注意输入的宽高是32x32，因为经过了第一次池化缩小了一半
        # 通道数翻倍的原因我是这么理解的：越深的层特征越复杂（比如从边缘到纹理到形状）
        # 所以需要更多卷积核来捕捉不同的特征组合
        # W_out = (32 + 2*1 - 3) / 1 + 1 = 32
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)

        # conv3: 输入(64, 16, 16) -> 输出(128, 16, 16)
        # 宽高16x16是经过两次池化后的结果
        # W_out = (16 + 2*1 - 3) / 1 + 1 = 16
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1)

        # ---- 池化层 ----

        # MaxPool2d就是在一个2x2的小窗口里取最大值
        # 效果就是宽和高各缩小一半
        # conv1后面: 64x64 -> 32x32
        # conv2后面: 32x32 -> 16x16
        # conv3后面: 16x16 -> 8x8
        # 为什么用max不用average：对于分类任务来说，MaxPool效果通常更好
        # 因为它关注的是"有没有这个特征"（取最大值），而不是"这个特征平均有多强"
        # 对锥桶这种目标来说，有没有边缘、色块特征比平均强度更重要
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # ---- 全连接层 ----

        # fc1: 输入8192 -> 输出256
        # 8192 = 128 * 8 * 8，就是conv3+pool之后的特征图展平
        # 一开始我算错了这个数，写成了128*4*4，结果跑的时候维度对不上报错了
        # 搞了半天才反应过来是池化了3次不是4次...
        self.fc1 = nn.Linear(in_features=128 * 8 * 8, out_features=256)

        # fc2: 输入256 -> 输出3
        # 3是因为有三个类别：blue、red、yellow
        # 输出的三个数就是三个类别的"分数"，哪个大就预测哪个
        # 注意这里不要加softmax！CrossEntropyLoss里面自带softmax
        # 我一开始加了softmax，loss死活不降，查了半天才知道重复了...
        self.fc2 = nn.Linear(in_features=256, out_features=3)

        # Dropout：训练的时候随机把60%的神经元关掉（输出变0）
        # 这样模型就不能只靠几个神经元，得学到更鲁棒的特征
        # 从0.5加大到0.6，更强的正则化防止过拟合
        # 注意：eval()模式下dropout会自动关闭，所以测试的时候不用管
        self.dropout = nn.Dropout(p=0.6)

    def forward(self, x):
        """
        前向传播，就是数据从输入流到输出的过程

        输入x: (batch_size, 3, 64, 64)  一批图片
        输出: (batch_size, 3)  每张图的三个类别分数
        """

        # conv1 + relu + pool
        # (B, 3, 64, 64) -> conv1 -> (B, 32, 64, 64) -> relu -> (B, 32, 64, 64) -> pool -> (B, 32, 32, 32)
        x = self.pool(F.relu(self.conv1(x)))

        # conv2 + relu + pool
        # (B, 32, 32, 32) -> conv2 -> (B, 64, 32, 32) -> relu -> pool -> (B, 64, 16, 16)
        x = self.pool(F.relu(self.conv2(x)))

        # conv3 + relu + pool
        # (B, 64, 16, 16) -> conv3 -> (B, 128, 16, 16) -> relu -> pool -> (B, 128, 8, 8)
        x = self.pool(F.relu(self.conv3(x)))

        # 展平：把(B, 128, 8, 8)拉成(B, 8192)
        # 因为全连接层只认一维向量，不认三维的特征图
        # x.size(0)就是batch_size，-1让pytorch自己算剩下多少
        x = x.view(x.size(0), -1)

        # fc1 + relu
        # (B, 8192) -> (B, 256)
        x = F.relu(self.fc1(x))

        # dropout，训练时随机关掉60%，测试时自动关闭
        x = self.dropout(x)

        # fc2输出层
        # (B, 256) -> (B, 3)
        # 输出3个类别的分数：blue、red、yellow
        # 这里千万别加softmax！！！
        x = self.fc2(x)

        return x


if __name__ == "__main__":

    # ---- 数据预处理 ----

    # 训练集的数据增强
    # 因为训练集才1298张图不算多，不加增强的话模型容易过拟合（训练集99%测试集70%那种）
    # 翻转和旋转之后相当于凭空多出来很多训练数据，模型泛化能力会好一些
    # 但是！数据增强只能对训练集做，测试集不能做，不然评估就不准了
    train_transforms = transforms.Compose(
        [
            # 统一缩放到64x64，因为原始图片尺寸不一样（blue有128x128的，red有64x64的）
            transforms.Resize([64, 64]),

            # 随机水平翻转，50%概率
            # 锥桶左右翻转还是锥桶，所以翻转不会改变类别
            transforms.RandomHorizontalFlip(p=0.5),

            # 随机旋转±15度
            # 我一开始设了30度，结果准确率反而掉了，可能是旋转太大锥桶变形太厉害了
            # 改成15度就好了
            transforms.RandomRotation(degrees=15),

            # 把PIL图片转成tensor，像素值从0-255变成0-1，形状从HWC变成CHW
            transforms.ToTensor(),

            # 标准化：把0-1映射到-1到1
            # 公式大概是 output = (input - 0.5) / 0.5
            # 这个必须加！！我一开始没加，loss卡在0.6不动，准确率50%等于瞎猜
            # 好像是因为输入全为正的话梯度方向会偏，不好优化
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ]
    )

    # 测试集只做基本的resize和归一化，不做增强
    test_transforms = transforms.Compose(
        [
            transforms.Resize([64, 64]),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ]
    )

    # ---- 超参数 ----

    BATCH_SIZE = 64   # 一开始用的1024，但训练集才1298张，一个batch就装完了，每个epoch只更新一次参数，太慢了
    EPOCH = 100       # 从200降到100，防止训练太久过拟合

    # ---- 加载数据 ----

    # ImageFolder会自动按文件夹名分类，blue=0, red=1, yellow=2（按字母顺序排的）
    trainset = datasets.ImageFolder(root=r'dataset/train', transform=train_transforms)
    testset1 = datasets.ImageFolder(root=r'dataset/test1', transform=test_transforms)
    testset2 = datasets.ImageFolder(root=r'dataset/test2', transform=test_transforms)

    print(f"训练集图片数量: {len(trainset)}")
    print(f"测试集1图片数量: {len(testset1)}")
    print(f"测试集2图片数量: {len(testset2)}")

    # DataLoader把数据分成batch，shuffle=True打乱顺序防止模型记住顺序
    train_loader = DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)
    test_loader1 = DataLoader(testset1, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)
    test_loader2 = DataLoader(testset2, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)

    # ---- 创建网络 ----

    # 有GPU用GPU没有用CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    net = mixed_net().to(device)

    # 打印网络结构，确认各层尺寸对不对
    summary(net, input_size=(1, 3, 64, 64), device=device)
    print(f'标签对应的ID: {trainset.class_to_idx}')

    # ---- 损失函数和优化器 ----

    # 交叉熵损失，分类任务基本都用这个
    # 它里面自带softmax，所以网络输出层不用加softmax
    criterion = nn.CrossEntropyLoss()

    # 用Adam优化器代替SGD
    # Adam会自适应调整每个参数的学习率（动量+RMSProp），收敛通常比纯SGD稳定且快
    # lr=0.001是默认值，适合这个任务
    # weight_decay从1e-4加大到5e-4，更强的L2正则化防止过拟合
    optimizer = optim.Adam(net.parameters(), lr=0.001, weight_decay=5e-4)

    # StepLR学习率调度器，每30个epoch学习率乘以0.1
    # 思路是前期用大步快速接近最优解，后期用小步精细调整防止震荡
    # epoch 1-30: lr=0.001
    # epoch 31-60: lr=0.0001
    # epoch 61-90: lr=0.00001
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

    # ---- 训练 ----

    max_correct = 0   # 记录test1最高准确率
    total_batches = len(train_loader)  # 每个epoch有多少个batch
    half_batches = total_batches // 2  # 一半的batch数，PPT要求"每训练完一半进行一次打印"
    print("Start")

    for epoch in range(EPOCH):
        # 切换训练模式，这步很重要！
        # train()模式dropout生效，eval()模式dropout关闭
        # 我一开始忘了切换，测试时dropout还在随机丢弃，准确率忽高忽低的
        net.train()

        train_loss = 0.0
        correct_train = 0
        total_train = 0

        for batch_id, (datas, labels) in enumerate(train_loader):
            # datas是图片，labels是标签(0=blue, 1=red, 2=yellow)
            # 必须把数据移到和网络同一个设备上，不然报错
            datas, labels = datas.to(device), labels.to(device)

            # 清空梯度，pytorch默认会累加梯度，不清零的话梯度会越来越大
            optimizer.zero_grad()

            # 前向传播：图片过网络得到预测分数
            outputs = net(datas)

            # 算loss
            loss = criterion(outputs, labels)

            # 反向传播：算梯度
            loss.backward()

            # 更新参数
            optimizer.step()

            # 统计训练loss和准确率
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, dim=1)   # 取分数最高的类别
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

            # PPT要求：每训练完一半进行一次打印
            # 就是每个epoch训练到一半batch的时候打印一次当前的loss和准确率
            if (batch_id + 1) == half_batches:
                mid_loss = train_loss / (batch_id + 1)
                mid_acc = 100.0 * correct_train / total_train
                print(f"epoch:{epoch + 1}\tbatch:{batch_id + 1}/{total_batches}\tloss:{mid_loss:.5f}\ttrain_acc:{mid_acc:.2f}%")

        # 每个epoch训练完后也打印一次（训练完另一半）
        train_acc = 100.0 * correct_train / total_train
        avg_loss = train_loss / total_batches
        print(f"epoch:{epoch + 1}\tbatch:{total_batches}/{total_batches}\tloss:{avg_loss:.5f}\ttrain_acc:{train_acc:.2f}%")

        # 更新学习率
        scheduler.step()

        # 每个epoch结束后在测试集上验证
        net.eval()
        os.makedirs("pth", exist_ok=True)
        correct1 = 0
        correct2 = 0
        total1 = 0
        total2 = 0

        with torch.no_grad():   # 测试时不需要算梯度，省内存
            for i, (datas1, labels1) in enumerate(test_loader1):
                datas1, labels1 = datas1.to(device), labels1.to(device)
                output_test1 = net(datas1)
                _, predicted1 = torch.max(output_test1.data, dim=1)
                total1 += labels1.size(0)
                correct1 += (predicted1 == labels1).sum().item()

            for i, (datas2, labels2) in enumerate(test_loader2):
                datas2, labels2 = datas2.to(device), labels2.to(device)
                output_test2 = net(datas2)
                _, predicted2 = torch.max(output_test2.data, dim=1)
                total2 += labels2.size(0)
                correct2 += (predicted2 == labels2).sum().item()

        c1 = correct1 / total1 * 100
        c2 = correct2 / total2 * 100
        print(f"\ttest1_acc:{c1:.2f}%\ttest2_acc:{c2:.2f}%")

        # test1准确率创新高就保存模型
        if c1 > max_correct:
            max_correct = c1
            MAX_PATH = f"pth/model_best_{max_correct:.2f}.pth"
            print(f"\tsave {MAX_PATH}")
            torch.save(net.state_dict(), MAX_PATH)
