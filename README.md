# STEPS
1. run either prep-img to create a virtual disk with the install or prep-disk to prepare the isntall for a read disk device
2. run mount-disk to mount the img (loop device) or the disk (sdx, or nvme) at /mnt
3. run install-base to install your void linux base system and packages, modify the file in packages to add more than a simple base system
4. run setup-config to pick your initial admin and user settings, modify the services folder to add or remove default services
5. run run-chroot to apply the config to the actual void linux install and install grub finalize the system
