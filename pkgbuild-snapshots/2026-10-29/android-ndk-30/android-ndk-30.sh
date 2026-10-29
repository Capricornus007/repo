# 注意：/etc/profile.d 下的 android-ndk-*.sh 是按檔名順序執行的，
# 23 → 27 → 30 依序 append，所以 `ndk-build` 這類直接走 PATH 的叫法會解析到
# **最後一個＝r30**。gradle／AGP 不受影響（它們按 ndkVersion 去 $ANDROID_HOME/ndk/<version> 找）。
export PATH="${PATH}:/opt/android-sdk/ndk/30.0.16248370"
