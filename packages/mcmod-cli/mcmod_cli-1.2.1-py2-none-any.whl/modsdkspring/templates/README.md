
# 模板布局

此目录存放在新建模组项目时所使用的所有资源。

* `configs/` —— 行为包/资源包的 JSON 清单文件。
* `project/scripts/` —— Python 脚本模板，会被渲染到生成的模组项目的 `scripts` 包中（如 `modMain.py`、系统入口点、共享配置等）。
* `framework/modsdkspring/` —— MODSDKSpring 框架源码，会被复制到生成项目的 `plugins/` 目录下。

每个文件夹的结构都与目标工作区中的结构相对应，因此可以单独更新或扩展模板，而无需修改无关的资源。
