const { createApp } = Vue;

createApp({
    data() {
        return {
            token: localStorage.getItem('token') || '',
            role: localStorage.getItem('role') || '',
            username: localStorage.getItem('username') || '',
            isRegisterView: false,

            // Notification states
            message: '',
            messageType: 'success',

            // Form data models
            authForm: { username: '', password: '', contact_details: '' },
            trekForm: { name: '', location: '', difficulty: '', duration: '', available_slots: '', start_date: '', end_date: '' },
            staffForm: { username: '', password: '', contact_details: '' },

            // Arrays for state data
            openTreks: [],
            staffTreks: []
        };
    },
    methods: {
        triggerNotification(msg, type = 'success') {
            this.message = msg;
            this.messageType = type;
            setTimeout(() => { this.message = ''; }, 4000);
        },
        async handleLogin() {
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: this.authForm.username, password: this.authForm.password })
                });
                const data = await response.get_json ? await response.get_json() : await response.json();

                if (!response.ok) throw new Error(data.error || 'Login failed');

                this.token = data.token;
                this.role = data.role;
                this.username = data.username;
                localStorage.setItem('token', data.token);
                localStorage.setItem('role', data.role);
                localStorage.setItem('username', data.username);

                this.authForm = { username: '', password: '', contact_details: '' };
                this.loadDashboardData();
            } catch (err) {
                this.triggerNotification(err.message, 'danger');
            }
        },
        async handleRegister() {
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.authForm)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Registration failed');

                this.triggerNotification("Registration complete! Please login.", "success");
                this.isRegisterView = false;
            } catch (err) {
                this.triggerNotification(err.message, 'danger');
            }
        },
        async loadDashboardData() {
            if (!this.token) return;

            if (this.role === 'Trekker') {
                const res = await fetch('/api/treks/open');
                this.openTreks = await res.json();
            } else if (this.role === 'Staff') {
                const res = await fetch('/api/staff/treks', {
                    headers: { 'Authorization': 'Bearer ${ this.token}' }
        });
this.staffTreks = await res.json();
            }
        },
        async bookTrek(trekId) {
    try {
        const response = await fetch('/api/book-trek', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ${ this.token}'
                    },
    body: JSON.stringify({ trek_id: trekId })
});
const data = await response.json();
if (!response.ok) throw new Error(data.error || 'Booking failed');

this.triggerNotification(data.message, "success");
this.loadDashboardData(); 
            } catch (err) {
    this.triggerNotification(err.message, 'danger');
}
        },
        async updateStaffTrek(trek) {
    try {
        const response = await fetch('/api/staff / trek / ${ trek.id }', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ${this.token}'
                    },
    body: JSON.stringify({ available_slots: trek.available_slots, status: trek.status })
});
if (!response.ok) throw new Error('Failed to save updates');
this.triggerNotification("Trek parameters modified successfully", "success");
            } catch (err) {
    this.triggerNotification(err.message, 'danger');
}
        },
        async createTrekRoute() {
    try {
        const response = await fetch('/api/admin/treks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ${ this.token}'
                    },
    body: JSON.stringify(this.trekForm)
});
if (!response.ok) throw new Error('Failed to create route');
this.triggerNotification("New Trek Published Successfully", "success");
this.trekForm = { name: '', location: '', difficulty: '', duration: '', available_slots: '', start_date: '', end_date: '' };
            } catch (err) {
    this.triggerNotification(err.message, 'danger');
}
        },
        async createStaffAccount() {
    try {
        const response = await fetch('/api/admin/add-staff', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ${this.token}'
                    },
    body: JSON.stringify(this.staffForm)
});
if (!response.ok) throw new Error('Failed to register staff');
this.triggerNotification("Staff account successfully active", "success");
this.staffForm = { username: '', password: '', contact_details: '' };
            } catch (err) {
    this.triggerNotification(err.message, 'danger');
}
        },

        async updateTrek(trek) {
            try {
                const response = await fetch('/api/admin/trek/update/${ trek.id }', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: trek.name,
                        location: trek.location,
                        difficulty: trek.difficulty,
                        duration: trek.duration,
                        available_slots: trek.available_slots,
                        status: trek.status,
                        assigned_staff_id: trek.assigned_staff_id
                    })
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Failed to update trek');

                alert("Trek updated successfully!");
                this.loadDashboardData(); // डेटा रिफ्रेश करने के लिए
            } catch (err) {
                alert(err.message);
            }
        },
logout() {
    this.token = '';
    this.role = '';
    this.username = '';
    localStorage.clear();
}
    },
mounted() {
    this.loadDashboardData();
}
}).mount('#app');