import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import LoginView from "../views/LoginView.vue";
import SignupView from "../views/SignupView.vue";
import AdminDashboard from "../views/Admin/AdminDashboard.vue";
import AdminTrek from "../views/Admin/AdminTrek.vue";
import UserDashboard from "../views/User/UserDashboard.vue";
import StaffDashboard from "../views/Staff/StaffDashboard.vue";
import BookingHistory from "../components/BookingHistory.vue";
import AdminStaff from "../views/Admin/AdminStaff.vue";
import AdminUsers from "../views/Admin/AdminUsers.vue";
import AdminStats from "../views/Admin/AdminStats.vue";
import UserProfile from "../views/User/UserProfile.vue";
import StaffProfile from "../views/Staff/StaffProfile.vue";
import UserBookings from "../views/User/UserBookings.vue";


const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'home', component: Home },
        { path: '/login', name: 'login', component: LoginView },
        { path: '/signup', name: 'signup', component: SignupView },
        { path: '/admin', name: 'admin', component: AdminDashboard, meta: { requiresRole: 'admin' } },
        { path: '/admin/treks', name: 'admin-treks', component: AdminTrek, meta: { requiresRole: 'admin' }  },
        { path: '/staff/:id', name: 'staff', component: StaffDashboard, meta: { requiresRole: 'staff' }  },
        { path: '/user/:id', name: 'user', component: UserDashboard, meta: { requiresRole: 'user' }  },
        { path: '/bookings', name: 'bookings', component: BookingHistory },
        { path: '/admin/staff', name: 'admin-staff', component: AdminStaff, meta: { requiresRole: 'admin' } },
        { path: '/admin/users', name: 'admin-users', component: AdminUsers, meta: { requiresRole: 'admin' } },
        { path: '/user/:id/profile', name: 'user-profile', component: UserProfile, meta: { requiresRole: 'user' }  },
        { path: '/staff/:id/profile', name: 'staff-profile', component: StaffProfile, meta: { requiresRole: 'staff' } },
        { path: '/admin/stats', name: 'admin-stats', component: AdminStats, meta: { requiresRole: 'admin' } },
        { path: '/user/:id/bookings', name: 'user-bookings', component: UserBookings, meta: { requiresRole: 'user' } },
    ]
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const userId = localStorage.getItem('user_id')
    const role = localStorage.getItem('role')

    if (to.meta.requiresRole && to.meta.requiresRole !== role) {
        if (!token || !role) {
            // not logged in at all — send to login
            return next('/login')
        }
        // logged in, just wrong role — bounce to their own home instead of logging out
        const home = { admin: '/admin', staff: `/staff/${userId}`, user: `/user/${userId}` }[role] || '/login'
        return next(home)
    }
    next()
})

export default router;