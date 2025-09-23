# KS3 SDK for python使用指南
---

## 安装

### 安装python sdk

#### 在线安装

	pip install ks3sdk

#### 本地安装

通过git下载SDK到本地，或者下载zip包后解压

	git clone https://gitee.com/ks3sdk/ks3-python-sdk.git

进入ks3-python-sdk目录，安装SDK

	cd ks3-python-sdk
	python setup.py install

## 初始化

    from ks3.connection import Connection
    ak = 'YOUR_ACCESS_KEY'
    sk = 'YOUR_SECRET_KEY'
    c = Connection(ak, sk, host='YOUR_REGION_ENDPOINT', is_secure=False, domain_mode=False,timeout = 1)

*常用参数说明*

+ ak：金山云提供的ACCESS KEY ID
+ sk：金山云提供的SECRET KEY ID
+ host：金山云提供的各个Region的域名（例
  ks3-cn-beijing.ksyuncs.com）,具体定义可参考 [API接口文档-Region(区域)](https://docs.ksyun.com/read/latest/65/_book/index.html)
+ is_secure：是否通过HTTPS协议访问Ks3，True:启用 False:关闭
+ domain_mode：是否使用自定义域名访问Ks3（host填写自定义域名），True:是 False:否
+ timeout：设置超时时间 ,默认10秒  单位:秒
## 运行环境

适用于2.6、2.7、3.3、3.4、3.5、3.6、3.7的Python版本

_推荐用3.5以上版本_

## 更多文档
* [快速入门](https://gitee.com/ks3sdk/ks3-python-sdk/blob/master/docs/GUIDE.md)
* [详细使用文档](https://gitee.com/ks3sdk/ks3-python-sdk/blob/master/docs/)
* [加密上传](https://gitee.com/ks3sdk/ks3-python-sdk/blob/master/docs/ENCRYPTION.md)
* [多线程分块上传下载](https://gitee.com/ks3sdk/ks3-python-sdk/blob/master/examples/multi.py)
* [金山云Python SDK文档](https://docs.ksyun.com/documents/40467)