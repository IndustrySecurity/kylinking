// 开发时调试用
// 在浏览器控制台执行此代码检查JWT令牌

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
}

// 检查localStorage中的令牌
function checkTokens() {
  const token = localStorage.getItem('token');
  const refreshToken = localStorage.getItem('refreshToken');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  console.log('===== DEBUG TOKEN INFO =====');
  console.log('User from localStorage:', user);
  console.log('Token exists:', !!token);
  console.log('RefreshToken exists:', !!refreshToken);
  
  if (token) {
    const decoded = parseJwt(token);
    console.log('Decoded token:', decoded);
    
    // 检查是否有管理员权限
    console.log('Has admin privileges:', decoded.is_admin || decoded.is_superadmin);
    
    // 检查令牌是否过期
    const exp = decoded.exp;
    const now = Math.floor(Date.now() / 1000);
    console.log('Token expired:', exp < now, `(${new Date(exp * 1000).toLocaleString()} vs ${new Date().toLocaleString()})`);
  }
  
  console.log('===========================');
  return { token, refreshToken, user };
}

// 执行检查
checkTokens(); 