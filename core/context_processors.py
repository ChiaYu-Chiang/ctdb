from django.contrib.auth.models import Group


def nav_menu_context(request):
    """
    為導航欄提供上下文信息
    
    返回值：
    {
        'is_t00_user': bool - 用戶是否屬於 T00 或 T00 的子部門（T11、T12 等）
        'user_departments': list - 用戶所屬的所有部門名稱列表
    }
    """
    is_t00_user = False
    user_departments = []
    
    if request.user.is_authenticated:
        # 獲取用戶所屬的所有部門
        user_groups = request.user.groups.all()
        user_departments = list(user_groups.values_list('name', flat=True))
        
        # 檢查用戶是否屬於 T00 或 T00 的子部門
        # T00 體系包括：T00、T11、T12、T13、T15 等所有 T 開頭的部門
        t00_departments = {'T00', 'T11', 'T12', 'T13', 'T15'}  # 根據實際情況調整
        
        if any(dept in user_departments for dept in t00_departments):
            is_t00_user = True
    
    return {
        'is_t00_user': is_t00_user,
        'user_departments': user_departments,
    }


# ============================================================================
# 可選：更高級的實現，支持動態獲取所有 T00 子部門
# 如果部門結構經常變化，可以使用這個版本
# ============================================================================

def nav_menu_context_advanced(request):
    """
    高級版本：動態檢查部門層級結構
    
    使用 GroupProfile.parent_department 字段，動態判斷用戶是否屬於 T00 體系。
    這樣即使新增加了子部門，也無需修改代碼。
    
    注意：此版本性能比簡單版本稍差（涉及數據庫查詢），但更靈活。
    """
    from accounts.models import GroupProfile  # 根據實際路徑調整
    
    is_t00_user = False
    user_departments = []
    
    if request.user.is_authenticated:
        # 獲取用戶所屬的所有部門
        user_groups = request.user.groups.all()
        user_departments = list(user_groups.values_list('name', flat=True))
        
        # 檢查用戶是否屬於 T00 或 T00 的子部門
        try:
            # 獲取 T00 部門
            t00_group = Group.objects.get(name='T00')
            
            # 檢查用戶是否直接屬於 T00
            if t00_group in user_groups:
                is_t00_user = True
            else:
                # 檢查用戶所屬的部門是否是 T00 的子部門
                # 通過檢查 parent_department 遞歸關係
                for user_group in user_groups:
                    try:
                        group_profile = GroupProfile.objects.select_related('parent_department').get(group=user_group)
                        
                        # 向上遍歷部門層級
                        current_group = group_profile.group
                        visited = set()  # 防止無限循環
                        
                        while current_group and current_group not in visited:
                            if current_group.name == 'T00':
                                is_t00_user = True
                                break
                            
                            visited.add(current_group)
                            
                            # 獲取父部門
                            try:
                                group_profile = GroupProfile.objects.get(group=current_group)
                                current_group = group_profile.parent_department
                            except GroupProfile.DoesNotExist:
                                break
                        
                        if is_t00_user:
                            break
                    except GroupProfile.DoesNotExist:
                        continue
        except Group.DoesNotExist:
            pass
    
    return {
        'is_t00_user': is_t00_user,
        'user_departments': user_departments,
    }