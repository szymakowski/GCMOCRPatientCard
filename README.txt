mountowanie dysku sieciowego lokalnie z root uprawnieniami
    sudo mount -t cifs //gcm1.pl/dokumenty_wspolne /mnt/gcm -o username=mszymakowski,uid=1000,gid=1000,rw,file_mode=0775,dir_mode=0775