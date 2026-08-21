# vmware_iso
去虚拟化成品系统，游戏多开板砖，自己没时间板砖额 
<br><br>
太大了上传了，没有开会员，再补充地址：<br>
成品vmware安装文件、替换文件、pc1系统需要上传到云盘才行，<br>




一、vmware版本<br>
vmware 16.1.2 build-17966106 <br>
win10虚拟机  内置 wegame  主玩天龙八部原始服。<br>
<img width="1916" height="1114" alt="image" src="https://github.com/user-attachments/assets/f1b70e52-428e-4d23-8ee7-2c13d3572140" /><br><br>

二、系统运行内存和cpu使用率。<br>
1、开机句柄数2W1，cpu 使用率2/%<br>
<img width="1691" height="931" alt="image" src="https://github.com/user-attachments/assets/0e502635-f615-4da2-85eb-d8278f0d0d67" /><br>
2、内存使用率460M左右<br>
<img width="1695" height="935" alt="image" src="https://github.com/user-attachments/assets/6fe84c54-7a08-4b60-bde5-f7a01ba59379" /><br><br>

三、系统去虚拟化程度<br>
<img width="1915" height="1070" alt="image" src="https://github.com/user-attachments/assets/b155823c-b2cf-4e79-8a4a-14f2d93e2645" /><br>

有2个没过<br>
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/774dc5e3-de76-4aa8-8add-2d88a718502b" /><br><br>

四、虚拟机多开方法<br>

一个ip最多开2个号，所以需要代理ip，自己自己买vpn 也可以自己搭建<br>
在自己的vps上面，vps买那种新客用户100多一年的配置也可以。<br>
用这个 socks5安装，可以起一个最小的socks5服务器，内存占用超级低。<br>

<img width="1690" height="930" alt="image" src="https://github.com/user-attachments/assets/3e0d6cdd-b419-41e5-8c30-534f172c2655" /><br>

<img width="1686" height="996" alt="image" src="https://github.com/user-attachments/assets/db6c3cf3-c41b-408c-99bc-073f5f5f00a2" /><br>

<img width="1400" height="915" alt="image" src="https://github.com/user-attachments/assets/56e494a4-acae-49ea-bb73-ce6bcc30c6d0" /><br><br>

五、游戏内运行游戏<br>
<img width="1910" height="1119" alt="image" src="https://github.com/user-attachments/assets/4bcd1372-875d-43df-a139-fc9cf31c1527" /><br>

<img width="1679" height="920" alt="image" src="https://github.com/user-attachments/assets/8b0663e0-4b8d-4195-ad8c-bde0a51ac96e" /><br><br>

六、克隆和修改克隆物理信息及系统激活<br>
用链接克隆多台虚拟机，克隆之后修改电脑信息、然后再激活win10<br>
<img width="1900" height="1048" alt="image" src="https://github.com/user-attachments/assets/c6df6987-faba-42a1-9e3b-6d59752076de" /><br>
<img width="1679" height="920" alt="image" src="https://github.com/user-attachments/assets/ead001c7-94bf-4ce8-a829-a61b52ca2c4b" /><br><br>

7、如果多开虚拟机物理机cpu使用率占用很高<br>
可以把这个三个ps脚本加载到计划任务。开机自动清理vmware lcx锁，清理系统垃圾，不管开几台，就拿开5台虚拟机，也是限定vmware总cpu使用是8个，物理机cpu使用率大于60%，限定为6个<br>
<img width="1910" height="120" alt="image" src="https://github.com/user-attachments/assets/8ca3e1ec-4953-42fa-bacf-b74da9873a45" /><br><br>


