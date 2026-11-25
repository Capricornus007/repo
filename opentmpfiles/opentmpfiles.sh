#!/bin/sh
# opentmpfiles —— tmpfiles.d 处理器（六最零血统重写 2026-11-25）
# 原版 opentmpfiles（OpenRC 生态）已死，本包功能续作：零 systemd 依赖。
# 用法:
#   opentmpfiles [--clean] [--exclude-dir=DIR]
#   默认: 执行创建/权限类指令；--clean: 额外执行年龄清理（q/Q/r/R）
# 文件层级（同名文件后者覆盖前者）:
#   /usr/lib/tmpfiles.d → /usr/local/lib/tmpfiles.d → /run/tmpfiles.d → /etc/tmpfiles.d
# 行格式: Type Path Mode User Group Age Argument
# 支持指令: f F w d D p L c b q Q r R x X z Z
set -eu

CLEAN=0
for a in "$@"; do
	case "$a" in
		--clean) CLEAN=1 ;;
		--exclude-dir=*) ;;  # 兼容占位
		*) echo "opentmpfiles: 未知参数 $a" >&2; exit 1 ;;
	esac
done

DIRS="${TMPFILES_DIRS:-/usr/lib/tmpfiles.d /usr/local/lib/tmpfiles.d /run/tmpfiles.d /etc/tmpfiles.d}"

msg() { echo "opentmpfiles: $*"; }
warn() { echo "opentmpfiles: 警告: $*" >&2; }

# ---- 占位符展开: %m 机器ID  %b 启动ID  %h 目标用户home ----
expand() {
	_s=$1
	if [ "${_s#*%}" != "$_s" ]; then
		_mid=""; [ -r /etc/machine-id ] && _mid=$(cat /etc/machine-id)
		_bid=""; [ -r /proc/sys/kernel/random/boot_id ] && _bid=$(cat /proc/sys/kernel/random/boot_id)
		_s=${_s//%m/$_mid}
		_s=${_s//%b/$_bid}
	fi
	echo "$_s"
}

# ---- 年龄 → 分钟（支持 s/m/h/d/w 与组合如 12h30m）；空 = 不清理 ----
age_to_min() {
	_a=$1
	[ -z "$_a" ] || [ "$_a" = "-" ] && { echo ""; return 0; }
	_total=0
	_num=
	_i=1
	_len=${#_a}
	while [ $_i -le $_len ]; do
		_c=$(printf '%s' "$_a" | cut -c$_i)
		case "$_c" in
			[0-9]*) _num="$_num$_c" ;;
			s|m|h|d|w)
				[ -z "$_num" ] && _num=1
				case "$_c" in
					s) _mult=0 ;;  # 秒级忽略（find 最小分钟）
					m) _mult=1 ;;
					h) _mult=60 ;;
					d) _mult=1440 ;;
					w) _mult=10080 ;;
				esac
				_total=$((_total + _num * _mult))
				_num=
				;;
			*) warn "年龄字段含未知字符 $_c（$_a）" ;;
		esac
		_i=$((_i + 1))
	done
	[ -n "$_num" ] && warn "年龄字段 $_a 末尾缺单位，忽略尾数"
	echo "$_total"
}

# ---- 解析 user/group 为 chown 可用形式；- = root ----
resolve_ug() {
	_u=$1; _g=$2
	[ "$_u" = "-" ] && _u=root
	[ "$_g" = "-" ] && _g=root
	echo "$_u:$_g"
}

# ---- 排除模式列表（x/X 累积，清理时跳过）----
EXCLUDES=""

do_create() {
	_type=$1; _path=$2; _mode=$3; _ug=$4; _arg=$5
	_path=$(expand "$_path")
	_arg=$(expand "${_arg:-}")
	[ "$_mode" = "-" ] && _mode=""
	case "$_type" in
		d)
			[ -d "$_path" ] || { msg "mkdir $_path"; mkdir -p "$_path"; }
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			;;
		D)
			msg "清空并建目录 $_path"
			rm -rf "$_path"; mkdir -p "$_path"
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			;;
		f|F)
			if [ "$_type" = F ] || [ ! -e "$_path" ]; then
				msg "写文件 $_path"
				[ -n "$_arg" ] && printf '%s' "$_arg" > "$_path" || : > "$_path"
			fi
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			;;
		w)
			[ -e "$_path" ] && { printf '%s' "$_arg" >> "$_path"; } || warn "w 目标不存在: $_path"
			;;
		p)
			[ -p "$_path" ] || { msg "mkfifo $_path"; mkfifo "$_path"; }
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			;;
		L)
			[ -e "$_path" ] || { msg "ln -s $_arg $_path"; ln -s "$_arg" "$_path" 2>/dev/null || warn "ln 失败: $_path"; }
			;;
		c|b)
			# argument = major:minor
			_maj=${_arg%%:*}; _min=${_arg##*:}
			[ -e "$_path" ] || {
				_t=c; [ "$_type" = b ] && _t=b
				msg "mknod $_path $_type $_maj:$_min"
				mknod "$_path" "$_t" "$_maj" "$_min" 2>/dev/null || warn "mknod 失败: $_path"
			}
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			;;
		q|Q)
			# 建目录 + 年龄清理（q 递归，Q 仅顶层）
			[ -d "$_path" ] || { msg "mkdir $_path"; mkdir -p "$_path"; }
			[ -n "$_mode" ] && chmod "$_mode" "$_path" 2>/dev/null || warn "chmod 失败: $_path"
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			[ "$CLEAN" = 1 ] && do_clean_path "$_path" "$6" "$_type"
			;;
		z|Z)
			[ -e "$_path" ] || { warn "z/Z 目标不存在: $_path"; return 0; }
			[ -n "$_mode" ] && chmod ${_type:+} "$_mode" "$_path" 2>/dev/null
			chown "$_ug" "$_path" 2>/dev/null || warn "chown 失败（需 root）: $_path"
			[ "$_type" = Z ] && chown -R "$_ug" "$_path" 2>/dev/null && [ -n "$_mode" ] && chmod -R "$_mode" "$_path" 2>/dev/null
			;;
		r|R)
			[ "$CLEAN" = 1 ] || return 0
			[ -e "$_path" ] || return 0
			msg "删除 $_path"
			[ "$_type" = R ] && rm -rf "$_path" || rm -f "$_path"
			;;
		x|X)
			EXCLUDES="$EXCLUDES $(expand "$_path")"
			;;
		*) warn "未知指令 $_type（$_path），跳过" ;;
	esac
}

# ---- 按年龄清理目录内容（q 递归 / Q 顶层）----
do_clean_path() {
	_path=$1; _age=$2; _type=$3
	_min=$(age_to_min "$_age")
	[ -n "$_min" ] || return 0
	[ "$_min" -gt 0 ] || return 0
	_maxd=""
	[ "$_type" = Q ] && _maxd="-maxdepth 1"
	# 组装 find 排除参数
	_prune=""
	for _x in $EXCLUDES; do
		_prune="$_prune -path $_x -prune -o"
	done
	msg "清理 $_path（${_min} 分钟前，${_type}）"
	# shellcheck disable=SC2086
	find "$_path" $_maxd $_prune -type f -mmin +"$_min" -exec rm -f {} \; 2>/dev/null
	find "$_path" $_maxd $_prune -type d -empty -mmin +"$_min" -delete 2>/dev/null
}

process_file() {
	_f=$1
	sed 's/[[:space:]]*#.*//' "$_f" | while read -r _line; do
		[ -n "$_line" ] || continue
		# shellcheck disable=SC2086
		set -- $_line
		_type=$1; _path=$2
		_mode=${3:--}; _user=${4:--}; _group=${5:--}; _age=${6:--}
		# argument = 第 7 字段起（可能含空格）
		_arg=""
		if [ $# -ge 7 ]; then
			# 重新取原始行第 7 字段之后
			_arg=$(printf '%s' "$_line" | cut -d' ' -f7-)
		fi
		_ug=$(resolve_ug "$_user" "$_group")
		# q/Q 的 age 传给清理；其余类型 age 忽略
		do_create "$_type" "$_path" "$_mode" "$_ug" "$_arg" "$_age"
	done
}

# 四层目录，同名文件后者覆盖前者
processed=""
for _dir in $DIRS; do
	[ -d "$_dir" ] || continue
	for _f in "$_dir"/*.conf; do
		[ -e "$_f" ] || continue
		_base=$(basename "$_f")
		case " $processed " in
			*" $_base "*) continue ;;
		esac
		msg "处理 $_f"
		process_file "$_f"
		processed="$processed $_base"
	done
done
