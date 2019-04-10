#!/bin/bash

usage_r()
{
    echo "-r: read something"
    echo "  -r --total: user total info"    #当前有多少用户，邮箱验证率，投票率，添加好友率，按等级排名
    echo "  -r --list: user simple info"    #简要信息，包括用户名，等级，邮箱验证，当前状态，注册时间，昵称等信息
    echo "    -r --list -o: user online/leave"
    echo "    -r --list -e: user emailvalid"
    echo "    -r --list -v: user voted"
    echo "  -r --vote: user vote info"          #投票简要信息，包括统计以及哪些用户参与了投票
    echo "  -r --forbid: current forbidden user"
    echo "  -r --forbad: past forbidden user"
    echo "  -r --handle: too old user"          #很久没操作的用户
    echo "  -r --user -b <username>: username base info"
    echo "  -r --user -v <username>: username vote info"
    echo "  -r --user -c <username>: username contact info"
    echo "  -r --user -ct <username> <otheruser>: chat info to otheruser" 
}

usage_d()
{
    echo "-d: delete something"
    echo "  -d <username>: delete user"  #关键信息，要再次确认
    echo "  -d -v <username>: delete user vote"
    echo "  -d -ct <username> [otheruser]: delete chats [or chat to someuser]"
    echo "  -d -l <username>"       #删除某用户的日志
}

usage_a()
{
    echo "-a: add something"
    echo "  -a <username>: add user"
}

usage_c()
{
    echo "-c: clear something"
    echo "  -c <username>: clear user"
    echo "  -c --limit <username>: clear limit of user"

}

usage()
{
    echo "======Usage======"
    echo "-h, --help: help"
    echo "-lmx: lottery for mx"
    echo "-lyz: lottery for yz"
    usage_r
    usage_d
    usage_a
    usage_c
}

if [ $# == 0 ]; then
    usage
fi

#操作数据库用到的相关参数
SQL_ACCOUNT=root
SQL_PASSWD=123456
SQL_DB=django_MyQQQ

#日志文件名称
LOG_FILE=/tmp/MyQ_log
DAY_DELETE=15

#以下标志用于分析记录脚本参数
read_flag=0
delete_flag=0
clear_flag=0
flag_2=0
flag_3=0
username=0
otheruser=0

mysql_handle()
{
    cmd=$1
    mysql -u $SQL_ACCOUNT -p$SQL_PASSWD $SQL_DB << EOF 2>> /dev/null 
$cmd
EOF
}

read_vote()     # $1为id, $2为username, 若$2为空则表示读取统计信息
{
    if [ $# == 2 ]; then
        id=$1
        user=$2
        mysql_handle "select vote_act from useradmin_vote where vote_id=$id and vote_user='$user'"
    elif [ $# == 1 ]; then
        id=$1
        mysql_handle "select vote_act from useradmin_vote where vote_id=$id and vote_user='<TJ>'"
    else
        :
    fi
}

delete_vote()   # $1为id, $2为username
{
    id=$1
    user=$2

    #1. 读取分析该用户的投票情况
    ret=`read_vote $id $user | sed -n '2,$p' | tr '}' '\n'`
    if [[ $ret == *select* ]]; then     #字符串包含
        :
    else
        echo "$user is not in vote_$id!"
        return
    fi

    cnt=1
    sel=''
    for line in $ret
    do
        # echo ${line##*select}     #表示截取select后的子串
        if [ $cnt -le 10 ]; then
            sel=${sel}${line:0-2:1}' '
            let "cnt+=1"
        else
            break
        fi
    done 
    sel_ary=($sel)              #数组元素下标从0开始喔
    echo "remove user($user): "${sel_ary[@]}
    # echo "================================"

    #2. 读取投票统计情况，需要减去上面用户的投票
    ret=`read_vote $id | sed -n '2,$p' | tr '}' '\n' | tr ' ' '-'`
    cnt=1
    vote_act='{"info": ['
    for line in $ret
    do
        # echo $line
        if [ $cnt -le 10 ]; then
            let num_A=${line##*\"A\":-} 2>> /dev/null
            if [ ${sel_ary[$cnt-1]} == 'A' ]; then
                let "num_A-=1"
            fi
            let num_B=${line##*\"B\":-} 2>> /dev/null
            if [ ${sel_ary[$cnt-1]} == 'B' ]; then
                let "num_B-=1"
            fi
            let num_C=${line##*\"C\":-} 2>> /dev/null
            if [ ${sel_ary[$cnt-1]} == 'C' ]; then
                let "num_C-=1"
            fi

            if [ $cnt -eq 10 ]; then
                vote_act=${vote_act}"{\"A\": $num_A, \"B\": $num_B, \"C\": $num_C, \"pos\": $cnt}], "
            else
                vote_act=${vote_act}"{\"A\": $num_A, \"B\": $num_B, \"C\": $num_C, \"pos\": $cnt}, "
            fi

            let "cnt+=1"
        else
            let remain=${line##*\"cnt\":-} 2>> /dev/null
            let "remain-=1"
            vote_act=${vote_act}"\"cnt\": $remain}"

            # echo $vote_act
            echo "remain: $remain"
            mysql_handle "update useradmin_vote set vote_act='$vote_act' where vote_id=$id and vote_user='<TJ>'"
            break;
            
        fi
        # echo "--------------------------"
    done
    
    mysql_handle "delete from useradmin_vote where vote_id=$id and vote_user='$user'"
}

delete_handle()
{
    if [ $# == 1 ]; then
        user=$1
        read -p "Are you sure to delete everything about user [$user]? Y/N: " ans
        if [ $ans == 'Y' ] || [ $ans == 'y' ]; then
            # 先确定用户是否存在
            ret=`mysql_handle "select count(*) from useradmin_useradmin where user_name='$user'" | sed -n '2,$p'`
            if [ $ret == 0 ]; then
                echo "Sorry, user [$user] is not registed."
                return
            fi
            # 删除日志
            echo "Delete log.."
            ret=`sed -e "/^$user\//d" $LOG_FILE`    
            echo "$ret" > $LOG_FILE
            # 删除投票
            echo "Delete vote.."
            delete_vote 1 $user
            delete_vote 2 $user
            # 删除chats表、news表、user表
            echo "Delete tables of chats, news, user.."
            ret=`mysql_handle "drop table chats_$user"`
            ret=`mysql_handle "drop table news_$user"`
            ret=`mysql_handle "drop table user_$user"`
            # 删除用户基本信息
            echo "Delete from useradmin.."
            ret=`mysql_handle "delete from useradmin_useradmin where user_name='$user'"`
            echo "Delete OK!"
        else
            echo "abort..."
        fi

    elif [ $# == 2 ]; then
        if [ $1 == "-v" ]; then
            read -p "Please input your vote type, mx/yz/all: " ans
            if [ $ans == 'mx' ]; then
                delete_vote 1 $2
            elif [ $ans == 'yz' ]; then
                delete_vote 2 $2
            elif [ $ans == 'all' ]; then
                delete_vote 1 $2
                delete_vote 2 $2
            else
                echo "abort..."
            fi
        elif [ $1 == '-l' ]; then
            ret=`sed -e "/^$2\//d" $LOG_FILE`
            echo "$ret" > $LOG_FILE
            echo "OK"
        elif [ $1 == "-ct" ]; then
            user=$2
            read -p "Are you sure to delete chats about user [$user]? Y/N: " ans
            if [ $ans == 'Y' ] || [ $ans == 'y' ]; then
                ret=`mysql_handle "delete from chats_$user"`
                if [ "$ret" == "" ]; then
                    echo "Delete ok."
                fi
            else
                echo "abort..."
            fi
        else
            :
        fi
    elif [ $# == 3 ]; then
        if [ $1 == '-ct' ]; then
            user=$2
            other=$3
            read -p "Are you sure to delete chats about user [$user] with [$other]? Y/N: " ans
            if [ $ans == 'Y' ] || [ $ans == 'y' ]; then
                ret=`mysql_handle "delete from chats_$user where name='$other'"`
                if [ "$ret" == "" ]; then
                    echo "Delete ok."
                fi
            else
                echo "abort..."
            fi
        fi
    else
        :
    fi
}

prase_base()
{   
    nickname=$1
    email=$2
    if [ $3 == 1 ]; then
        gender='男'
    elif [ $3 == 2 ]; then
        gender='女'
    elif [ $3 == 3 ]; then
        gender='保密'
    else
        return 1
    fi

    register_time=$4" "${5:0:8}

    if [ $6 == 0 ]; then
        sign='保密'
    elif [ $6 == 1 ]; then
        sign='水瓶'
    elif [ $6 == 2 ]; then
        sign='双鱼'
    elif [ $6 == 3 ]; then
        sign='白羊'
    elif [ $6 == 4 ]; then
        sign='金牛'
    elif [ $6 == 5 ]; then
        sign='双子'
    elif [ $6 == 6 ]; then
        sign='巨蟹'
    elif [ $6 == 7 ]; then
        sign='狮子'
    elif [ $6 == 8 ]; then
        sign='处女'
    elif [ $6 == 9 ]; then
        sign='天秤'
    elif [ $6 == 10 ]; then
        sign='天蝎'
    elif [ $6 == 11 ]; then
        sign='射手'
    elif [ $6 == 12 ]; then
        sign='摩羯'
    else
        return 1
    fi

    echo "nickname: $nickname"
    echo "email: $email"
    echo "gender: $gender"
    echo "register time: $register_time"
    echo "sign: $sign"
}

prase_vote()
{
    echo " "
    if [ $1 == 1 ]; then
        echo "=======马小同学会======"
    elif [ $1 == 2 ];then
        echo "=======姚中同学会======"
    else
        :
    fi
    echo " "

    abc=$2
    if [ $abc == 'A' ];then
        ans="A. 五一、元旦等小长假"
    elif [ $abc == 'B' ];then
        ans="B. 国庆假期"
    elif [ $abc == 'C' ];then
        ans="C. 过年前后"
    else
        :
    fi

    echo -n "1. 你觉得同学会的时间在何时举行比较好？"
    echo $ans

    abc=$3
    if [ $abc == 'A' ];then
        ans="A. 初一~初三"
    elif [ $abc == 'B' ];then
        ans="B. 初三~初五"
    elif [ $abc == 'C' ];then
        ans="C. 初六及以后"
    else
        :
    fi

    echo -n "2. 如果在年后举行同学会，你通常什么时候有空？"
    echo $ans

    abc=$4
    if [ $abc == 'A' ];then
        ans="A. 100~200"
    elif [ $abc == 'B' ];then
        ans="B. 200~400"
    elif [ $abc == 'C' ];then
        ans="C. 400~600"
    else
        :
    fi

    echo -n "3. 你认为每人交多少钱合适？"
    echo $ans

    abc=$5
    if [ $abc == 'A' ];then
        ans="A. 吃饭、唱歌等常规形式"
    elif [ $abc == 'B' ];then
        ans="B. 户外活动、附近旅游"
    elif [ $abc == 'C' ];then
        ans="C. 打牌、台球、娱乐"
    else
        :
    fi

    echo -n "4. 你期望的同学会形式是？"
    echo $ans

    abc=$6
    if [ $abc == 'A' ];then
        ans="A. 均摊"
    elif [ $abc == 'B' ];then
        ans="B. 大家自愿出多少就多少"
    elif [ $abc == 'C' ];then
        ans="C. ---"
    else
        :
    fi

    echo -n "5. 同学会的费用是否应该均摊？"
    echo $ans

    abc=$7
    if [ $abc == 'A' ];then
        ans="A. 愿意"
    elif [ $abc == 'B' ];then
        ans="B. 不是很愿意"
    elif [ $abc == 'C' ];then
        ans="C. 看情况"
    else
        :
    fi

    echo -n "6. 如果有晚上唱K环节，你愿意一起玩到后半夜吗？"
    echo $ans

    abc=$8
    if [ $abc == 'A' ];then
        ans="A. 吃饭能凑一桌就行"
    elif [ $abc == 'B' ];then
        ans="B. 吃饭能凑两桌"
    elif [ $abc == 'C' ];then
        ans="C. 吃饭能凑三桌"
    else
        :
    fi

    echo -n "7. 多少人以上的同学会，你愿意去？"
    echo $ans

    abc=$9
    if [ $abc == 'A' ];then
        ans="A. 可以的"
    elif [ $abc == 'B' ];then
        ans="B. 还是不要，自费吧"
    elif [ $abc == 'C' ];then
        ans="C. ---"
    else
        :
    fi

    echo -n "8. 将同学会费用拿出一部分买烟、零食等，你同意吗？"
    echo $ans
    abc=${10}
    if [ $abc == 'A' ];then
        ans="A. 马金"
    elif [ $abc == 'B' ];then
        ans="B. 开化"
    elif [ $abc == 'C' ];then
        ans="C. 随便啦"
    else
        :
    fi

    echo -n "9. 你觉得在哪举行同学会比较好？"
    echo $ans

    abc=${11}
    if [ $abc == 'A' ];then
        ans="A. 支持"
    elif [ $abc == 'B' ];then
        ans="B. 不去了吧，主要是同学的友谊"
    elif [ $abc == 'C' ];then
        ans="C. 不去了吧，母校已不是当年的母校"
    else
        :
    fi

    echo -n "10. 去母校看看怎么样？"
    echo $ans
}

read_handle()
{
    if [ $# == 1 ]; then
        if [ $1 == '--total' ]; then
            ret=`mysql_handle 'select count(*) from useradmin_useradmin' | sed -n '2,$p'` 
            echo "Total $ret register user."
            total=$ret
            ret=`mysql_handle 'select count(*) from useradmin_useradmin where user_emailValid=1' | sed -n '2,$p'`
            if [ $ret != 0 ]; then
                let rate=ret*100/total
                echo "Email verified($ret: $rate%)"
            else
                echo "No user Email is verified."
            fi

            ret=`mysql_handle 'select count(*) from useradmin_vote where vote_id=1 and vote_user!="<TJ>"' | sed -n '2,$p'`
            if [ $ret != 0 ]; then
                let rate=ret*100/total
                echo "Vote mx($ret: $rate%)"
            else
                echo "No user take part in vote_mx."
            fi

            ret=`mysql_handle 'select count(*) from useradmin_vote where vote_id=2 and vote_user!="<TJ>"' | sed -n '2,$p'`
            if [ $ret != 0 ]; then
                let rate=ret*100/total
                echo "Vote yz($ret: $rate%)"
            else
                echo "No user take part in vote_yz."
            fi
            echo "----------------------------"

            ret=`mysql_handle 'select concat_ws(": ", user_level, user_name) from useradmin_useradmin order by user_level desc' | sed -n '2,$p'`
            echo "User level:"
            echo "$ret"

        elif [ $1 == '--list' ]; then
            ret=`mysql_handle 'select user_name as name, user_level as level, user_emailValid as emailV, 
                user_status as status, replace(left(register_time,19), " ",",") as register_time, user_nickname as nickname
                from useradmin_useradmin'`
            #需要特别注意echo $ret 和 echo "$ret" 结果有所不同，后者才会原样输出
            echo "----------------------------------------------------------------------------------"
            echo "$ret" | while read line
            do 
                printf "| %-18s| %-8s| %-8s| %-8s| %-20s| %-20s\n" $line
                echo "----------------------------------------------------------------------------------"
            done
        elif [ $1 == '--vote' ]; then
            ret=`mysql_handle 'select count(*) from useradmin_vote where vote_user="<TJ>" and vote_id=1'`
            id_1=`echo "$ret" | tail -n 1`
            if [ $id_1 == 1 ]; then
                echo "[MX is voted]"
                ret=`mysql_handle 'select vote_user from useradmin_vote where vote_id=1'`
                name_list=`echo "$ret" | sed -n '2,$p'`
                # echo $name_list
                cnt=0
                for i in $name_list
                do
                    if [ $i != '<TJ>' ]; then
                        echo "  $i"
                        let "cnt+=1"
                    fi
                done
                echo "[Total: $cnt]"
            else
                echo "MX is not yet voted!"
            fi
            echo "---------------"

            ret=`mysql_handle 'select count(*) from useradmin_vote where vote_user="<TJ>" and vote_id=2'`
            id_2=`echo "$ret" | tail -n 1`
            if [ $id_2 == 1 ]; then
                echo "[YZ is voted]"
                ret=`mysql_handle 'select vote_user from useradmin_vote where vote_id=2'`
                name_list=`echo "$ret" | sed -n '2,$p'`
                # echo $name_list
                cnt=0
                for i in $name_list
                do
                    if [ $i != '<TJ>' ]; then
                        echo "  $i"
                        let "cnt+=1"
                    fi
                done
                echo "[Total: $cnt]"
            else
                echo "YZ is not yet voted!"
            fi
        elif [ $1 == '--forbid' ]; then
            ret=`mysql_handle 'select user_name from useradmin_useradmin where limit_reason != 0'`
            if [[ $ret == *user_name* ]]; then
                ret=`echo "$ret" | sed -n '2,$p'`
                echo "The current limit user:"
                echo "----------------------"
                echo "$ret"
            else
                echo "No limit user now."
            fi
        elif [ $1 == '--forbad' ]; then     #曾经受过限制的用户，需要去日志文件里查看
            ret=`cat $LOG_FILE | grep REQ_TOO_OFTEN`
            echo "$ret"
        elif [ $1 == '--handle' ]; then
            ret=`mysql_handle "select user_name, handle_time from useradmin_useradmin order by handle_time" | sed -n '2,$p'`
            echo "$ret" | while read line
            do
                grep_handle $line
                if [ $? -ne 0 ]; then
                    break
                fi
            done
        else
            usage_r
        fi

        return 0
    fi

    if [ $# == 2 ]; then
        if [ $1 == "--list" ] && [ $2 == "-o" ]; then
            ret=`mysql_handle 'select user_name from useradmin_useradmin where user_status != 0'`
            if [[ $ret == user_name* ]]; then
                echo "The below user is online or leave:"
                ret=`echo "$ret" | sed -n '2,$p'`
                echo "$ret"
            else
                echo "All user is offline."
            fi
        
        elif [ $1 == "--list" ] && [ $2 == "-e" ]; then
            ret=`mysql_handle 'select user_name from useradmin_useradmin where user_emailValid = 1' | sed -n '2,$p'`
            echo "The below user is email verified:"
            echo "$ret"
            echo "---------------------------------"
            ret=`mysql_handle 'select user_name from useradmin_useradmin where user_emailValid = 0' | sed -n '2,$p'`
            echo "The below user is email unverified:"
            echo "$ret"
            echo "---------------------------------"
        elif [ $1 == "--list" ] && [ $2 == "-v" ]; then
            ret=`mysql_handle 'select concat_ws(": ", vote_user, vote_point) from useradmin_vote where vote_id=1 and vote_user != "<TJ>"' | sed -n '2,$p'`
            echo "The opinion of vote_1:"
            echo "---------------------"
            echo "$ret"
            echo "====================="
            ret=`mysql_handle 'select concat_ws(": ", vote_user, vote_point) from useradmin_vote where vote_id=2 and vote_user != "<TJ>"' | sed -n '2,$p'`
            echo "The opinion of vote_2:"
            echo "---------------------"
            echo "$ret"
        else
            usage_r
        fi
    fi 

    if [ $# == 3 ]; then
        if [ $1 == "--user" ] && [ $2 == "-b" ]; then
            ret=`mysql_handle "select user_nickname, user_email, user_gender, register_time, user_sign from useradmin_useradmin where user_name='$3'"`
            if [[ $ret == user_nickname* ]]; then
                ret=`echo "$ret" | sed -n '2,$p'`
                ret=`prase_base $ret`
                echo "$ret"
            else
                echo "User $3 is not exist."
            fi
        elif [ $1 == "--user" ] && [ $2 == "-c" ]; then
            user=$3
            ret=$(mysql_handle "select concat_ws(': ', name, nickname) from user_$user where relation = 0" | sed -n '2,$p')
            if [ "$ret" != "" ]; then
                echo "===>Friend:"
                echo "$ret"
            fi
            ret=$(mysql_handle "select concat_ws(': ', name, nickname) from user_$user where relation = 1" | sed -n '2,$p')
            if [ "$ret" != "" ]; then
                echo "===>Stranger:"
                echo "$ret"
            fi

            ret=$(mysql_handle "select user_blacklist from useradmin_useradmin where user_name='$user'" | sed -n '2,$p')
            if [ "$ret" != "" ]; then
                echo "===>Blacklist:"
                echo "$ret"
            fi
        elif [ $1 == "--user" ] && [ $2 == "-v" ]; then
            user=$3
            for id in `seq 2`
            do
                #投票行为
                ret=`read_vote $id $user | sed -n '2,$p' | tr '}' '\n'`
                if [[ $ret == *select* ]]; then     #字符串包含
                    :
                else
                    continue
                fi

                cnt=1
                sel=''
                for line in $ret
                do
                    if [ $cnt -le 10 ]; then
                        sel=${sel}${line:0-2:1}' '
                        let "cnt+=1"
                    else
                        break
                    fi
                done 
                sel_ary=($sel)              
                prase_vote $id" " "${sel_ary[@]}"

                #个人观点
                ret=$(mysql_handle "select vote_point from useradmin_vote where vote_id=$id and vote_user='$user'" | sed -n '2,$p')
                if [ $ret != "" ]; then
                    echo -e "\nPersonal point: $ret"
                fi
            done
        else
            usage_r
        fi
    fi

    if [ $# == 4 ]; then
        if [ $1 == "--user" ] && [ $2 == "-ct" ]; then
            user=$3
            other=$4
            ret=`mysql_handle "select replace(left(chat_time, 19), ' ', ','), io, message from chats_$user where name='$other'" | sed -n '2,$p'`
            last_day=''
            echo "$ret" | while read line
            do
                cnt=1
                dir=0
                for item in $line
                do
                    if [ $cnt -eq 1 ]; then
                        day=${item:0:10}
                        if [ "$day" != "$last_day" ]; then
                            last_day=$day
                            echo "------------"
                            echo -n "$item "
                        else
                            echo -n "           ${item:11:8} "
                        fi
                    elif [ $cnt -eq 2 ]; then
                        dir=$item
                        if [ $item == 0 ]; then
                            echo "$user --> $other"
                        else
                            echo "$user <-- $other"
                        fi
                        echo -n -e "\t"
                    else
                        if [ $dir == 0 ]; then
                            echo -n "$item "
                        else
                            echo -n -e "\033[33m${item} \033[0m"
                        fi
                    fi
                    let "cnt+=1"
                done
                echo ""
            done
        else
            usage_r
        fi
    fi
}

add_handle()
{
    user=$1
    #1. 先判断用户名的格式是否正确
    if [[ $user =~ ^[a-zA-Z_][0-9a-zA-Z_]{6,16}$ ]]; then
        :   #pass
    else
        echo "错误: 用户名要求包含英文字符、数字、下划线，非数字开头，6~16个字符"
        return
    fi

    # 确定用户是否存在
    ret=`mysql_handle "select count(*) from useradmin_useradmin where user_name='$user'" | sed -n '2,$p'`
    if [ $ret == 1 ]; then
        echo "Sorry, user [$user] is exist."
        return
    fi

    #2. 判断昵称的格式
    while true
    do
        read -p "请输入昵称(:quit退出): " nickname
        if [ $nickname == ':quit' ]; then 
            echo ""
            return 
        fi

        if [[ $nickname =~ [a-zA-Z0-9_]{3,8}$ ]]; then
            break
        else
            echo "错误: 昵称格式错误，要求包含英文字符、数字、下划线，3~8长度"
            continue
        fi
    done

    #3. 判断密码的格式
    while true
    do
        read -s -p "请输入密码(:quit退出): " passwd
        if [ $passwd == ':quit' ]; then 
            echo ""
            return 
        fi
        echo ""
        read -s -p "请再次输入密码(:quit退出): " passwd_again
        if [ $passwd_again == ':quit' ]; then 
            echo ""
            return 
        fi
        echo ""

        if [ $passwd != $passwd_again ]; then
            echo "错误: 两次密码不一致"
            continue
        else
            if [[ $passwd =~ [0-9a-zA-Z_]{6,16}$ ]]; then
                break
            else
                echo "错误: 密码格式错误，要求包含英文字符、数字、下划线，6~16个字符"
                continue
            fi
        fi
    done

    #4. 判断Email的格式
    while true
    do
        read -p "请输入Email(:quit退出): " email
        if [ $email == ':quit' ]; then 
            echo ""
            return 
        fi

        if [[ $email =~ ^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$ ]]; then
            ret=`mysql_handle "select count(*) from useradmin_useradmin where user_email='$email'" | sed -n '2,$p'`
            if [ $ret == 1 ]; then
                echo "警告: 邮箱$email已存在."
                continue
            else
                break
            fi
        else
            echo "错误: Eamil格式错误"
            continue
        fi
    done

    #5. 获取星座
    echo "星座——"
    echo "0:保密, 1:水瓶, 2:双鱼, 3:白羊, 4:金牛, 5:双子, 6:巨蟹, 7:狮子, 8:处女, 9:天秤, 10:天蝎, 11:射手, 12:摩羯"
    while true
    do
        read -p "请输入星座编号: " sign
        if [ $sign -ge 0 ] && [ $sign -le 12 ]; then
            break
        else
            continue
        fi
    done

    #6. 获取性别
    echo "性别——"
    echo "1:男, 2:女, 3:保密"
    while true
    do
        read -p "请输入性别编号: " gender
        if [ $gender -ge 1 ] && [ $gender -le 3 ]; then
            break
        else
            continue
        fi
    done

    # echo "$user $nickname $passwd $email $sign $gender"
    mysql_handle "insert into useradmin_useradmin (\`user_name\`,\`user_nickname\`,\`user_password\`,\`user_email\`,\`user_sign\`,\`user_gender\`,\`user_level\`,\`user_emailValid\`,\`user_status\`,\`limit_reason\`,\`register_time\`,\`login_time\`,\`handle_time\`,\`user_blacklist\`,\`forget_randomint\`,\`forget_trycnt\`, \`forget_time\`,\`setting_permitSearch\`,\`setting_permitAdd\`) values('$user', '$nickname', '$passwd', '$email', $sign, $gender, 0, 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '', 0, 0, CURRENT_TIMESTAMP, 1, 0);"
    echo "Insert into useradmin_useradmin.."

    # 接下去需要创建相关表格
    mysql_handle "create table news_$user(\`id\` int(11) not null auto_increment, \`news_time\` datetime(6) not null, \`classtype\` int(11) not null, \`status\` int(11) not null, \`action\` int(11) not null, \`info_main\` varchar(32) binary, \`info_minor\` varchar(128) binary, primary key(\`id\`)) comment='by shell'"

    mysql_handle "create table user_$user(\`id\` int(11) not null auto_increment, \`name\` varchar(32) unique not null, \`relation\` int(11) not null, \`status\` int(11) not null, \`nickname\` varchar(32) not null, \`remark\` varchar(32) not null, \`email\` varchar(254) unique not null, \`gender\` int(11) not null, \`sign\` int(11) not null, primary key(\`id\`)) comment='by shell' "

    mysql_handle "create table chats_$user(\`id\` int(11) not null auto_increment, \`name\` varchar(32) not null, \`io\` int(11) not null, \`chat_time\` datetime(6) not null, \`chat_type\` int(11) not null, \`in_status\` int(11) not null, \`message\` varchar(128) not null, primary key(\`id\`))comment='by shell' "
    echo "Create tables.."

    ret=`mysql_handle "select concat('\"', user_nickname, '\"'), user_email, user_gender, user_sign from useradmin_useradmin where user_name='MyQ_jiantong'" | sed -n '2,$p'`
    ret_arry=( $ret )
    nickname_peer=${ret_arry[0]}
    email_peer=${ret_arry[1]}
    gender_peer=${ret_arry[2]}
    sign_peer=${ret_arry[3]}
    mysql_handle "insert into user_$user(\`name\`, \`relation\`, \`status\`, \`nickname\`, \`remark\`, \`email\`, \`gender\`, \`sign\`) values('MyQ_jiantong', 0, 0, '$nickname_peer', '', '$email_peer', '$gender_peer', '$sign_peer')"
    mysql_handle "insert into user_MyQ_jiantong(\`name\`, \`relation\`, \`status\`, \`nickname\`, \`remark\`, \`email\`, \`gender\`, \`sign\`) values('$user', 0, 0, '$nickname', '', '$email', '$gender', '$sign')"

}

clear_handle()
{
    if [ $# == 1 ]; then
        user=$1
        # 先确定用户是否存在
        ret=`mysql_handle "select count(*) from useradmin_useradmin where user_name='$user'" | sed -n '2,$p'`
        if [ $ret == 0 ]; then
            echo "Sorry, user [$user] is not registed."
            return
        fi
        # 复位useradmin_useradmin相关项目
        echo "Clear of user [$user]"
        echo "Reset useradmin_useradmin.."
        ret=`mysql_handle "update useradmin_useradmin set user_level=0, user_status=0, limit_reason=0, user_blacklist='' where user_name='$user'"`
        # 删除投票
        echo "Delete vote.."
        delete_vote 1 $user
        delete_vote 2 $user
        # 清空chats表、news表、user表
        echo "Clear tables of chats, news, user.."
        ret=`mysql_handle "truncate table chats_$user"`
        ret=`mysql_handle "truncate table news_$user"`
        ret=`mysql_handle "truncate table user_$user"`
        echo "Clear OK."
    elif [ $# == 2 ]; then
        if [ $1 == '--limit' ]; then
            user=$2
            ret=`mysql_handle "update useradmin_useradmin set limit_reason=0 where user_name='$user'"`
            echo "Clear OK."
        else
            usage_c
        fi
    else
        usage_c
    fi
}


if [ $1 == '-a' ] && [ $# == 2 ]; then  
        add_handle $2
        return
fi

grep_handle()
{
    user=$1
    now=`date +%s`
    past=`date --date "$2 $3" +%s`

    let "diff=now-past"
    let "day=diff/(60*60*24)"
    
    if [ $day -gt $DAY_DELETE ]; then
        echo "$user: ${day} days ago."
        return 0
    else
        return 1
    fi
}

lottery_handle()
{
    id=$1
    ret=`mysql_handle "select vote_user from useradmin_vote where vote_id=$id and vote_user != '<TJ>'" | sed -n '2,$p'`
    num_arry=()
    cnt=0
    for item in $ret
    do
        if [ $item == '_MyQ_jiantong' ]; then    #排除在外
            continue
        else
            num_arry[$cnt]=$item
            let "cnt+=1"
        fi
    done

    if [ $id == 1 ]; then
        school='马小'
    elif [ $id == 2 ]; then
        school='姚中'
    else
        :
    fi

    echo "参与$school同学会投票的有${#num_arry[@]}人，如下:"
    echo ${num_arry[@]}
    sleep 2
    echo ""
    echo "好的，下面开始抽出第1位￥5红包幸运奖。。。输入z和回车结束"

    pos=0
    tput sc
    while true
    do
        echo -n "    ${num_arry[$pos]} "
        # sleep 1
        read -t 0.1 tmp
        if [[ $tmp == "z" ]]; then
            tput rc
            tput ed
            echo "恭喜! ${num_arry[$pos]}"
            luck_1=${num_arry[$pos]}
            sleep 2
            break
        fi
        tput rc
        tput ed
        let "pos+=1"
        if [ $pos -ge ${#num_arry[@]} ]; then
            pos=0
        fi
    done

    num_arry=()
    cnt=0
    for item in $ret
    do
        if [ $item == '_MyQ_jiantong' ] || [ $item == $luck_1 ]; then    #排除在外
            continue
        else
            num_arry[$cnt]=$item
            let "cnt+=1"
        fi
    done
    # echo ${num_arry[@]}
    echo "下面开始抽出第2位￥5红包幸运奖。。。输入z和回车结束"
    pos=0
    tput sc
    while true
    do
        echo -n "    ${num_arry[$pos]} "
        # sleep 1
        read -t 0.1 tmp
        if [[ $tmp == "z" ]]; then
            tput rc
            tput ed
            echo "恭喜! ${num_arry[$pos]}"
            luck_2=${num_arry[$pos]}
            sleep 2
            break
        fi
        tput rc
        tput ed
        let "pos+=1"
        if [ $pos -ge ${#num_arry[@]} ]; then
            pos=0
        fi
    done

    num_arry=()
    cnt=0
    for item in $ret
    do
        if [ $item == '_MyQ_jiantong' ] || [ $item == $luck_1 ] || [ $item == $luck_2 ]; then    #排除在外
            continue
        else
            num_arry[$cnt]=$item
            let "cnt+=1"
        fi
    done
    # echo ${num_arry[@]}
    echo "最后，抽出1位￥10红包幸福奖。。。输入z和回车结束"
    pos=0
    tput sc
    while true
    do
        echo -n "    ${num_arry[$pos]} "
        # sleep 1
        read -t 0.1 tmp
        if [[ $tmp == "z" ]]; then
            tput rc
            tput ed
            echo "恭喜! ${num_arry[$pos]}"
            sleep 1
            echo "感谢大家参与！"
            break
        fi
        tput rc
        tput ed
        let "pos+=1"
        if [ $pos -ge ${#num_arry[@]} ]; then
            pos=0
        fi
    done
}

#main, 下面开始遍历分析脚本参数
for i in $@
do
    if [ $i == 'test' ] && [ $# == 1 ]; then
        :
        # ret=`mysql_handle "select concat('\"', user_nickname, '\"'), user_email, user_gender, user_sign from useradmin_useradmin where user_name='MyQ_jiantong'" | sed -n '2,$p'`
        # echo "$ret"
    elif [ $i == '-h' ] || [ $i == '--help' ]; then
        usage
        break
    elif [ $i == '-r' ] && [ $# == 1 ]; then
        usage_r
        break
    elif [ $i == '-d' ] && [ $# == 1 ]; then
        usage_d
        break
    elif [ $i == '-a' ] && [ $# == 1 ]; then
        usage_a
        break
    elif [ $i == '-c' ] && [ $# == 1 ]; then
        usage_c
        break
    elif [ $i == '-lmx' ] && [ $# == 1 ]; then
        lottery_handle 1
        break
    elif [ $i == '-lyz' ] && [ $# == 1 ]; then
        lottery_handle 2
        break
    else
        if [ $read_flag == 1 ]; then    #读相关
            if [ $flag_2 == 0 ]; then
                flag_2=$i
                if [ $# == 2 ]; then
                    read_handle $flag_2     #2个参数的情况
                    break
                fi
            else
                if [ $flag_3 == 0 ]; then
                    flag_3=$i
                    if [ $# == 3 ]; then
                        read_handle $flag_2 $flag_3     #3个参数的情况
                        break
                    fi
                else
                    if [ $username == 0 ]; then
                        username=$i
                        if [ $# == 4 ]; then
                            read_handle $flag_2 $flag_3 $username   #4个参数的情况
                            break
                        fi
                    else
                        if [ $# == 5 ]; then
                            otheruser=$i
                            read_handle $flag_2 $flag_3 $username $otheruser    #5个参数的情况
                        else
                            usage_r
                        fi
                        break
                    fi
                fi
            fi
        elif [ $delete_flag == 1 ]; then        #删除相关
            if [ $flag_2 == 0 ]; then
                flag_2=$i
                if [ $# == 2 ]; then
                    delete_handle $flag_2       #2个参数的情况
                    break
                fi 
            else
                if [ $flag_3 == 0 ]; then
                    flag_3=$i
                    if [ $# == 3 ]; then
                        delete_handle $flag_2 $flag_3     #3个参数的情况
                        break
                    fi
                else
                    if [ $# == 4 ]; then
                        delete_handle $flag_2 $flag_3 $i   #4个参数的情况
                        break
                    fi
                fi
            fi
        elif [ $clear_flag == 1 ]; then
            if [ $flag_2 == 0 ]; then
                flag_2=$i
                if [ $# == 2 ]; then
                    clear_handle $flag_2
                    break
                fi
            else
                if [ $flag_3 == 0 ]; then
                    flag_3=$i
                    if [ $# == 3 ]; then
                        clear_handle $flag_2 $flag_3
                        break
                    else
                        usage_c
                        break
                    fi
                fi
            fi
        elif [ $clear_flag == 0 ] && [ $i == '-c' ]; then
            clear_flag=1
        elif [ $read_flag == 0 ] && [ $i == '-r' ]; then
            read_flag=1
        elif [ $delete_flag == 0 ] && [ $i == '-d' ]; then
            delete_flag=1
        else
            usage
        fi
    fi
done
