import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import LoginView from "../views/LoginView.vue";
import SignupView from "../views/SignupView.vue";
import HelloWorld from "../components/HelloWorld.vue";
import AdminDashboard from "../views/Admin/AdminDashboard.vue";
import UserDashboard from "../views/User/UserDashboard.vue";
import StaffDashboard from "../views/Staff/StaffDashboard.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'home', component: Home },
        { path: '/hello', name: 'hello', component: HelloWorld },
        { path: '/login', name: 'login', component: LoginView },
        { path: '/signup', name: 'signup', component: SignupView },
        { path: '/admin', name: 'admin', component: AdminDashboard},
        { path: '/staff', name: 'staff', component: StaffDashboard },
        { path: '/user', name: 'user', component: UserDashboard },
    ]
});

export default router;