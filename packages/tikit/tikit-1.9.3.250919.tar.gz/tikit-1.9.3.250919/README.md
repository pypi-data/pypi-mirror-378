TiKit是一套对接腾讯云TI平台各模块的python SDK工具。 
Tikit的核心作用是为了让算法类研发人员在使用Notebook功能时，能够更好地进行交互，打通Notebook和本地环境访问平台的路径，进行从训练到推理的闭环。

# 发布
'''bash
# 公网
make publish
'''

# 开发
'''bash
yum install -y cyrus-sasl cyrus-sasl-devel cyrus-sasl-lib krb5-devel
pip install -r requirements.txt
'''
# 公网
pip install tikit -U -i https://pypi.org/simple
'''