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

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'home', component: Home },
        { path: '/login', name: 'login', component: LoginView },
        { path: '/signup', name: 'signup', component: SignupView },
        { path: '/admin', name: 'admin', component: AdminDashboard},
        { path: '/admin/treks', name: 'admin-treks', component: AdminTrek },
        { path: '/staff/:id', name: 'staff', component: StaffDashboard },
        { path: '/user/:id', name: 'user', component: UserDashboard },
        { path: '/bookings', name: 'bookings', component: BookingHistory },
        { path: '/admin/staff', name: 'admin-staff', component: AdminStaff },
        { path: '/admin/users', name: 'admin-users', component: AdminUsers }
    ]
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const userId = localStorage.getItem('user_id')
    const role = localStorage.getItem('role')

    if (to.meta.requiresRole && to.meta.requiresRole !== role) {
        localStorage.clear()
        return next('/login')
    }
    next()
})

export default router;