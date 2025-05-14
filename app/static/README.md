# 静态文件目录

这个目录用于存放网站的静态文件，如图片、CSS、JavaScript等。

## favicon.ico

请在此目录下放置一个favicon.ico文件，可以通过以下方式获取：

1. 使用在线工具生成favicon.ico，如 https://www.favicon-generator.org/
2. 使用项目logo制作favicon.ico
3. 下载一个现成的favicon.ico文件并放在此目录

示例命令（在Windows PowerShell中）：
```powershell
Invoke-WebRequest -Uri "https://www.google.com/favicon.ico" -OutFile "app/static/favicon.ico"
```

或者在命令提示符中：
```cmd
curl -o app/static/favicon.ico https://www.google.com/favicon.ico
```
