# SEU自动化框架

## To Do List
- [x] 入校申请
- [x] 请假申请
- [x] 每日上报
- [ ] 讲座预约
- [ ] 场馆预约

## 文档结构
```
SEU_LOGIN
├── config(存放配置信息，除acounts.json之外均与每个脚本对应)
│   ├── acounts.json(用户名、密码和用于推送的Barkkey)
│   ├── admission.json
│   ├── leave.json
│   └── report.json
├── tool(用于登录的工具)
│   ├── encrypt.js
│   ├── encrypt.py
│   ├── encrypt_bak.py(给没法装js2py的小伙伴，需要PyExecJS)
│   └── login.py
├── README.md
├── admission.py(入校申请)
├── leave.py(请假申请)
├── report.py(每日上报)
└── requirements.txt
```

## 特性
适用不同主流平台，包括`Windows`,`Linux`,`MacOs`以及其他的自动化脚本管理系统

## Github Action
您也可以使用Github Action运行相关的脚本，具体步骤如下：
1. 首先 fork 本项目到自己的仓库

2. 进入 Actions -> Enable Workflow

3. .github/workflows中的工作流仅供参考

4. 修改 Config文件夹中的相关个人信息

5. 如果担心隐私泄露，可以进入 Settings -> Secrets -> New repository secret，创建若干secret（对应config文件夹中的json），将json内容复制进去，名字就是相对应的json文件名。
