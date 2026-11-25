#!/bin/sh
# opensysusers —— sysusers.d 处理器（六最零血统重写 2026-11-25）
# 原版 opensysusers（OpenRC 生态）已死，本包是其功能续作：零 systemd 依赖。
# 处理 sysusers.d 片段，创建系统用户/组。幂等：已存在即跳过。
# 指令集（systemd sysusers.d 子集）:
#   u <name> <uid> <comment> <home> <shell>   创建用户（uid 可为 -、数字、或 min:max 区间取首个空闲）
#   g <name> <gid>                            创建组（gid 可为 -、数字、min:max）
#   m <user> <group>                          把 user 加入 group
# 文件层级（后者覆盖前者同名文件）: /usr/lib/sysusers.d → /usr/local/lib/sysusers.d → /etc/sysusers.d
set -eu

SYSDIRS="/usr/lib/sysusers.d /usr/local/lib/sysusers.d /etc/sysusers.d"

msg() { echo "opensysusers: $*"; }
warn() { echo "opensysusers: 警告: $*" >&2; }

# 取指定区间内首个未占用的 uid/gid；$1=min $2=max $3=类型(user|group)
first_free_id() {
	_min=$1; _max=$2; _type=$3
	_i=$_min
	while [ "$_i" -le "$_max" ]; do
		if [ "$_type" = user ]; then
			getent passwd "$_i" >/dev/null 2>&1 || { echo "$_i"; return 0; }
		else
			getent group "$_i" >/dev/null 2>&1 || { echo "$_i"; return 0; }
		fi
		_i=$((_i + 1))
	done
	return 1
}

# 解析 uid/gid 字段：- / 数字 / min:max
resolve_id() {
	_spec=$1; _type=$2
	case "$_spec" in
		-) echo "-" ;;
		*:*) _lo=${_spec%%:*}; _hi=${_spec##*:}
			first_free_id "$_lo" "$_hi" "$_type" || warn "区间 $_spec 无空闲 id（$_type）" ;;
		*) echo "$_spec" ;;
	esac
}

do_u() {
	_name=$1; _uid=$2; _gecos=$3; _home=$4; _shell=$5
	getent passwd "$_name" >/dev/null 2>&1 && return 0
	_rid=$(resolve_id "$_uid" user)
	[ "$_rid" = "-" ] && _rid=""
	# 组名同名组：systemd 语义是 useradd 默认建同名组
	if ! getent group "$_name" >/dev/null 2>&1; then
		msg "创建组 $_name"
		groupadd -r "$_name" 2>/dev/null || groupadd "$_name"
	fi
	msg "创建用户 $_name${_rid:+ (uid=$_rid)}"
	# -r 系统用户；home 缺省 /；shell 缺省 nologin
	useradd -r ${_rid:+-u "$_rid"} -c "${_gecos:-}" \
		-d "${_home:-/}" -s "${_shell:-/usr/sbin/nologin}" -M "$_name"
}

do_g() {
	_name=$1; _gid=$2
	getent group "$_name" >/dev/null 2>&1 && return 0
	_rid=$(resolve_id "$_gid" group)
	[ "$_rid" = "-" ] && _rid=""
	msg "创建组 $_name${_rid:+ (gid=$_rid)}"
	groupadd -r ${_rid:+-g "$_rid"} "$_name" 2>/dev/null || groupadd "$_name"
}

do_m() {
	_user=$1; _group=$2
	getent group "$_group" >/dev/null 2>&1 || { warn "组 $_group 不存在，跳过 m $_user"; return 0; }
	if id -nG "$_user" 2>/dev/null | tr ' ' '\n' | grep -qx "$_group"; then
		return 0
	fi
	msg "把 $_user 加入 $_group"
	gpasswd -a "$_user" "$_group" >/dev/null
}

process_file() {
	_f=$1
	# 跳过注释与空行；行内 # 后为注释
	sed 's/[[:space:]]*#.*//' "$_f" | while read -r _line; do
		[ -n "$_line" ] || continue
		# shellcheck disable=SC2086
		set -- $_line
		_op=$1; shift || true
		case "$_op" in
			u) [ $# -ge 1 ] && do_u "$@" || warn "u 参数不足: $_line" ;;
			g) [ $# -ge 1 ] && do_g "$@" || warn "g 参数不足: $_line" ;;
			m) [ $# -ge 2 ] && do_m "$@" || warn "m 参数不足: $_line" ;;
			*) warn "未知指令 $_op（$_f），跳过" ;;
		esac
	done
}

# 三层目录按优先级处理：/usr/lib → /usr/local/lib → /etc（同名文件后者覆盖前者，即只处理后者）
processed=""
for _dir in $SYSDIRS; do
	[ -d "$_dir" ] || continue
	for _f in "$_dir"/*.conf; do
		[ -e "$_f" ] || continue
		_base=$(basename "$_f")
		case " $processed " in
			*" $_base "*) continue ;;  # 已被更高优先级层处理
		esac
		msg "处理 $_f"
		process_file "$_f"
		processed="$processed $_base"
	done
done
