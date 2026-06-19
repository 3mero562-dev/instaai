const BASE_URL = 'https://instaai-iz25.onrender.com'// إدارة التوكن

const saveToken = (token) => localStorage.setItem('jwt_token', token);
const getToken = () => localStorage.getItem('jwt_token');
const removeToken = () => localStorage.removeItem('jwt_token');

// التحقق من الدخول
function checkAuth() {
    if (!getToken()) {
        window.location.href = 'login.html';
    }
}

// طلبات API الموحدة
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
    };

    const config = {
        method,
        headers,
    };

    if (body) config.body = JSON.stringify(body);

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'حدث خطأ في الطلب');
        return data;
    } catch (err) {
        alert(err.message);
        return null;
    }
}

// تسجيل الدخول
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            saveToken(data.access_token);
            window.location.href = 'dashboard.html';
        } else {
            alert(data.detail);
        }
    });
}

// إنشاء حساب
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const data = await fetchAPI('/api/auth/register', 'POST', { email, password });
        if (data) {
            alert('تم إنشاء الحساب بنجاح، يمكنك الدخول الآن');
            window.location.href = 'login.html';
        }
    });
}

// تحميل بيانات الداشبورد
async function loadDashboard() {
    const user = await fetchAPI('/api/user/me');
    if (user) {
        document.getElementById('userName').innerText = user.name || 'مستخدم';
        document.getElementById('botStatusLabel').innerText = user.botStatus ? 'نشط' : 'متوقف';
        document.getElementById('botStatusLabel').style.color = user.botStatus ? 'var(--success)' : 'var(--danger)';
        document.getElementById('pageIdLabel').innerText = user.instagramPageId || 'غير مضبوط';
    }
}

// تحميل الإعدادات
async function loadSettings() {
    const user = await fetchAPI('/api/user/me');
    if (user) {
        document.getElementById('botStatus').checked = user.botStatus || false;
        document.getElementById('businessDescription').value = user.businessDescription || '';
        document.getElementById('aiInstructions').value = user.aiInstructions || '';
        document.getElementById('instagramPageId').value = user.instagramPageId || '';
        document.getElementById('instagramAccessToken').value = user.instagramAccessToken || '';
    }
}

// تحديث الإعدادات
if (document.getElementById('settingsForm')) {
    document.getElementById('settingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
    bot_status: document.getElementById('botStatus').checked ? "enabled" : "disabled",
    business_description: document.getElementById('businessDescription').value,
    ai_instructions: document.getElementById('aiInstructions').value,
    instagram_page_id: document.getElementById('instagramPageId').value,
    instagram_access_token: document.getElementById('instagramAccessToken').value
};

        const data = await fetchAPI('/api/user/settings', 'PATCH', body);
        if (data) {
            alert('تم حفظ الإعدادات بنجاح');
        }
    });
}

// خروج
function logout() {
    removeToken();
    window.location.href = 'login.html';
}