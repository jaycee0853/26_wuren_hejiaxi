import torch
from torchvision import transforms,datasets
from torch.utils.data.dataloader import DataLoader
from net import mixed_net  # 从net.py导入网络定义

def test_model(model_path, test_loader):
    """
    加载模型然后测试，打印整体准确率和每个类别的准确率
    """

    # 有GPU用GPU没有用CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 创建网络，结构必须和训练时一模一样
    model = mixed_net()

    # 加载训练好的参数
    # map_location=device 这个参数很重要
    # 如果模型是在GPU上训练的但测试时只有CPU，不加这个会报错
    # 我就踩过这个坑...
    model.load_state_dict(torch.load(model_path, map_location=device))

    # 切换到评估模式！！这步不能忘
    # eval()会关闭Dropout，不然测试的时候还在随机丢弃神经元，结果会忽高忽低
    model.eval()

    # 把模型放到设备上
    model.to(device)

    # 统计每个类别预测对了多少
    # 3个类别：blue=0, red=1, yellow=2（ImageFolder按字母顺序排的）
    class_correct = list(0. for i in range(3))
    class_total = list(0. for i in range(3))

    # 测试时不需要算梯度，关掉可以省内存加速
    with torch.no_grad():
        for i, (datas, labels) in enumerate(test_loader):
            # 数据要移到和模型同一个设备上
            datas, labels = datas.to(device), labels.to(device)

            # 前向传播得到预测分数
            output_test = model(datas)

            # 取分数最高的类别作为预测结果
            _, predicted1 = torch.max(output_test.data, dim=1)

            # 看预测对了没有
            matches = (predicted1 == labels)

            # 逐个样本统计
            for i in range(len(labels)):
                label = labels[i]
                class_correct[label] += matches[i].item()
                class_total[label] += 1

    # 算整体准确率
    total_correct = sum(class_correct)
    total = sum(class_total)
    accuracy = 100.0 * total_correct / total
    print(f'Overall Accuracy: {accuracy:.2f}%')

    # 算每个类别的准确率
    # class 0 = blue, class 1 = red, class 2 = yellow
    for i in range(3):
        print(f'Accuracy of Class {i}: {100 * class_correct[i] / class_total[i]:.2f}%')


# ---- 测试集预处理 ----
# 测试集不做数据增强！只做resize和归一化
transforms = transforms.Compose([
    transforms.Resize([64, 64]),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# ---- 加载测试数据 ----
BATCH_SIZE = 1024  # 测试时batch可以大点，反正不存梯度
testset1 = datasets.ImageFolder(root=r'dataset/test1', transform=transforms)
testset2 = datasets.ImageFolder(root=r'dataset/test2', transform=transforms)
test_loader1 = DataLoader(testset1, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)
test_loader2 = DataLoader(testset2, batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)

# ---- 运行测试 ----
# 把model_path改成你训练出来的模型文件路径
model_path = r"pth/model_best_99.54.pth"
test_model(model_path, test_loader1)
test_model(model_path, test_loader2)
