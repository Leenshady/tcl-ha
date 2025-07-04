# TCL空调
https://bbs.hassbian.com/thread-29746-1-1.html
本插件可将TCL空调设备接入HomeAssistant，理论上支持所有小程序设备。
主要用来适配本人的小蓝鸟空调，小程序不支持的设备需要获取设备zip配置文件进行适配，工作量大切手头也没那么多tcl设备所以目前不准备适配。
目前手头家居大多都换上小米设备了，不出问题的话可能较长时间都不会更新

使用抓包工具抓到小程序登录时的account_id和refreshToken即可

感谢[banto6](https://github.com/banto6/haier)提供的参考
## 已支持实体
- Switch
- Number
- Select
- Sensor

## 安装

方法1：下载并复制`custom_components/tcl`文件夹到HomeAssistant根目录下的`custom_components`文件夹即可完成安装

方法2：已经安装了HACS，可以点击按钮快速安装 [![通过HACS添加集成](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ndwzy&repository=tcl&category=integration)

## 配置

配置 > 设备与服务 >  集成 >  添加集成 > 搜索`tcl`

或者点击: [![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=tcl)


## 调试
在`configuration.yaml`中加入以下配置来打开调试日志。

```yaml
logger:
  default: warn
  logs:
    custom_components.tcl: debug
```
