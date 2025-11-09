#!/bin/bash
ipaddress=$1
version=$2
OS=$3
LOG_DIR="vcenter_logs"
UP_DIR="update"
PROJECT_PATH="/home/vimec/v-center-testing/"
VLOG_FILE="/home/vimec/log/v-center.log"
RELEASE_INFO="/home/vimec/vic/conf/release.info"
DATE=$(date '+%Y-%m-%d')
FILENAME="V-center_"$version"_"$DATE"_log.log"
ZIP_URL="http://download.vimec.priv/download.php?version=$version&distribution=OS-10"
COREDUMPPATH="/var/coredump/"
COREFILENAME="V-center_"$version"_"$DATE"_coredump_list.txt"
RELEASE_VERSION=$(awk -F= '/^\[VIC-KERNEL\]/{f=1; next} /^\[/{f=0} f && /^Version=/{print $2}' /home/vimec/vic/conf/release.info)
REF="3.20.0.0"

if [[ $version == *"-RC"* ]]; then
  RELEASE_CANDIDATE="E:/DATA/Vimec/Projects/application/v-center-linux/release-candidates/$version/$OS"
else
   RELEASE_CANDIDATE="E:/DATA/Vimec/Projects/application/v-center-linux/releases/$version/$OS" 
fi
echo $RELEASE_CANDIDATE
TARGET_BACKUP_PATH="E:/DATA/Vimec/Projects/application/Test_backup/DO_NOT_TOUCH"
ADMIN_PATH="/home/admin/update"
ADMIN_BACKUP_PATH="/home/admin/backup"
ARC_BACKUP_PATH="/home/admin/backup/archive"
date=$(date '+%Y-%m-%d')

kill_vcenter(){
    echo "Kill vecnter"
    if [ "$(printf '%s\n' "$REF" "$RELEASE_VERSION" | sort -V | tail -n1)" = "$RELEASE_VERSION" ]; then
        echo "Release version $RELEASE_VERSION is greater than $REF"
        ssh root@$ipaddress "/home/vimec/scripts/killvcenter"
    else
        echo "Release version $RELEASE_VERSION is less than $REF"
        ssh root@$ipaddress "/home/vimec/vic/killvcenter"
    fi
}

startvic(){
    echo "Start VCenter"
    if [ "$(printf '%s\n' "$REF" "$RELEASE_VERSION" | sort -V | tail -n1)" = "$RELEASE_VERSION" ]; then
        echo "Release version $RELEASE_VERSION is greater than $REF"
        ssh root@$ipaddress "export DISPLAY=\":0\";/home/vimec/scripts/vcenter 1>/dev/null 2>/dev/null &"
    else
        echo "Release version $RELEASE_VERSION is less than $REF"
	    ssh root@$ipaddress "export DISPLAY=\":0\";/home/vimec/vic/startvic 1>/dev/null 2>/dev/null &"
    fi
    sleep 2m
}

cleareventlog(){
    echo "Clear event log"
    if [ "$(printf '%s\n' "$REF" "$RELEASE_VERSION" | sort -V | tail -n1)" = "$RELEASE_VERSION" ]; then
        echo "Release version $RELEASE_VERSION is greater than $REF"
        ssh root@$ipaddress "/home/vimec/scripts/cleareventlog"
    else
        echo "Release version $RELEASE_VERSION is less than $REF"
        ssh root@$ipaddress "/home/vimec/vic/cleareventlog"
    fi

}

clearcoredumplog(){
    echo "Delete core dump"
    ssh root@$ipaddress "find $COREDUMPPATH -name *core* -mtime -1 -type f -delete"
}

install_buster_package() {
    mkdir -p $UP_DIR
    echo "Copy latest package from fileserver"
    ssh root@$ipaddress "rm -f $ADMIN_PATH/*.deb"
    scp dc-01:$RELEASE_CANDIDATE/*.deb $UP_DIR/ || exit 1
    scp $UP_DIR/*.deb root@$ipaddress:$ADMIN_PATH
    ssh root@$ipaddress "dpkg --force-all -i $ADMIN_PATH/*.deb"
    rm -f $UP_DIR/*.deb || exit 1
}

copy_send_eventlog(){
    mkdir -p $LOG_DIR
    echo "Copy the v-center log"
    ssh root@$ipaddress "mkdir -p $PROJECT_PATH/$LOG_DIR"
    ssh root@$ipaddress "cp $VLOG_FILE $PROJECT_PATH/$LOG_DIR/$FILENAME"
    
    if [ -f $LOG_DIR ]; then
        echo "File $LOG_DIR exists."
        scp -r root@$ipaddress:$PROJECT_PATH/$LOG_DIR/$FILENAME $LOG_DIR/$FILENAME
    else
        echo "File $DIR does not exist."
        mkdir -p $LOG_DIR
        echo "The $LOG_DIR folder is created"
        scp -r root@$ipaddress:$PROJECT_PATH/$LOG_DIR/$FILENAME $LOG_DIR/$FILENAME
    fi
}

copy_send_coredumplog(){
    echo "Save core dump list"
    ssh root@$ipaddress "find $COREDUMPPATH -mtime -1 -type f -print > $PROJECT_PATH/$LOG_DIR/$COREFILENAME"
    echo "Copy core dump list"
    scp -r root@$ipaddress:$PROJECT_PATH/$LOG_DIR/$COREFILENAME $LOG_DIR/$COREFILENAME
}   

copy_backup_files(){
    mkdir backup
    echo "Copy backup folder"
    scp dc-01:$TARGET_BACKUP_PATH/*.tgz backup/ || exit 1
    ssh root@$ipaddress "mkdir -p $ARC_BACKUP_PATH"
    ssh root@$ipaddress "mv $ADMIN_BACKUP_PATH/*.tgz $ARC_BACKUP_PATH"
    scp backup/*.tgz root@$ipaddress:$ADMIN_BACKUP_PATH
    echo "Copied all backup files" 
}

download_install_buster_package(){
    ssh root@$ipaddress "rm -f $ADMIN_PATH/*.deb"
    ssh root@$ipaddress "wget -O '$ADMIN_PATH/buster-$version.zip' 'http://download.vimec.priv/download.php?version=$version&distribution=OS-10'"
    ssh root@$ipaddress "unzip '$ADMIN_PATH/buster-$version.zip' -d '$ADMIN_PATH'"
    ssh root@$ipaddress "rm '$ADMIN_PATH/buster-$version.zip'"
    ssh root@$ipaddress "dpkg --force-all -i $ADMIN_PATH/*.deb"
}
