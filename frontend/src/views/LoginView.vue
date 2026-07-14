<template>
    <div class="vh-100 d-flex flex-column">
        <div class="row g-0 flex-grow-1">

            <!-- ── Left panel: form ── -->
            <div class="col-lg-6 d-flex flex-column justify-content-center px-5 py-4 overflow-auto bg-white">
                <div class="mx-auto w-100" style="max-width: 380px;">
                    <img :src="icon" alt="TrekAssist" class="login-icon d-block mx-auto mb-3" />
                    <h1 class="fw-bold mb-1">Welcome Back!</h1>
                    <p class="text-muted mb-4">Login to continue your trekking journey</p>

                    <form @submit.prevent="login()">
                        <div class="input-group mb-3">
                            <span class="input-group-text bg-white text-muted">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <rect x="2" y="4" width="20" height="16" rx="2" />
                                    <path d="M2 6l10 7 10-7" />
                                </svg>
                            </span>
                            <input
                                id="email"
                                v-model="formdata.email"
                                type="email"
                                class="form-control"
                                placeholder="Email address"
                                autocomplete="username"
                                required
                            >
                        </div>

                        <div class="input-group mb-3">
                            <span class="input-group-text bg-white text-muted">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <rect x="4" y="10" width="16" height="10" rx="2" />
                                    <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                                </svg>
                            </span>
                            <input
                                id="password"
                                v-model="formdata.password"
                                :type="showPassword ? 'text' : 'password'"
                                class="form-control"
                                placeholder="Password"
                                autocomplete="current-password"
                                required
                            >
                            <button
                                type="button"
                                class="input-group-text bg-white text-muted"
                                @click="showPassword = !showPassword"
                                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                            >
                                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
                                    <circle cx="12" cy="12" r="3" />
                                </svg>
                                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.6 21.6 0 0 1 5.06-5.94M9.9 4.24A10.6 10.6 0 0 1 12 4c7 0 11 7 11 7a21.6 21.6 0 0 1-2.16 3.19" />
                                    <path d="M14.12 14.12A3 3 0 1 1 9.88 9.88" />
                                    <path d="M1 1l22 22" />
                                </svg>
                            </button>
                        </div>

                        <button type="submit" class="btn btn-brand w-100 py-2 fw-bold rounded-3 mb-3">Login</button>

                        <p class="text-center text-muted small mb-0">
                            Don't have an account?
                            <router-link to="/signup" class="text-brand fw-bold text-decoration-none">Sign up</router-link>
                        </p>
                    </form>
                </div>
            </div>

            <!-- ── Right panel: image + quote ── -->
            <div class="col-lg-6 d-none d-lg-block position-relative login-right" :style="{ backgroundImage: `url(${loginBg})` }">
                <div class="login-right-overlay h-100 d-flex flex-column justify-content-start p-5">
                    <div class="quote-block text-white" style="max-width: 260px;">
                        <span class="quote-mark d-block">&ldquo;</span>
                        <p class="fs-4 fw-semibold mt-2 mb-3">The best view comes after the hardest climb.</p>
                        <span class="quote-underline d-block"></span>
                    </div>
                </div>
            </div>

        </div>

        <router-link to="/" class="back-home position-fixed top-0 start-0 m-4 text-muted text-decoration-none small">
            &larr; Back to Home
        </router-link>
    </div>
</template>

<script>
import axios from 'axios'
import icon from '../assets/icon.png'
import loginBg from '../assets/loginBG.png'

export default {
    data() {
        return {
            icon,
            loginBg,
            showPassword: false,
            formdata: {
                email: "",
                password: ""
            }
        }
    },
    methods: {
        async login() {
            try {
                const resp = await axios.post("http://127.0.0.1:5000/login", this.formdata)
                localStorage.clear()
                localStorage.setItem('token', resp.data.token)
                localStorage.setItem('user_id', resp.data.user_id)
                localStorage.setItem('role', resp.data.role)
                localStorage.setItem('username', resp.data.username)
                if (resp.data.role === "admin")
                    this.$router.push('/admin')
                else if (resp.data.role === "staff")
                    this.$router.push(`/staff/${resp.data.user_id}`)
                else if (resp.data.role === "user")
                    this.$router.push(`/user/${resp.data.user_id}`)
                else
                    this.$router.push('/signup')
            } catch (err) {
                if (err.response?.status === 404) {
                    alert(err.response.data.msg || "User not found")
                    this.$router.push('/signup')
                } else {
                    alert(err.response?.data?.msg || "Login failed")
                }
            }
        }
    }
}
</script>

<style scoped>
.login-icon {
    height: 75px;
    width: auto;
    object-fit: contain;
}
.text-brand {
    color: #4169e1;
}
.btn-brand {
    background: #4169e1;
    border-color: #4169e1;
    color: #fff;
}
.btn-brand:hover {
    background: #3557c2;
    border-color: #3557c2;
    color: #fff;
}
.form-control:focus {
    border-color: #4169e1;
    box-shadow: 0 0 0 0.2rem rgba(65,105,225,0.15);
}
.input-group:focus-within .input-group-text {
    border-color: #4169e1;
}

.login-right {
    background-size: cover;
    background-position: center;
}
.login-right-overlay {
    background: linear-gradient(180deg, rgba(65,105,225,0.15) 0%, rgba(17,24,39,0.35) 100%);
}
.quote-mark {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    color: #aebdf2;
}
.quote-underline {
    width: 40px;
    height: 3px;
    background: #4169e1;
    border-radius: 2px;
}

.back-home {
    z-index: 10;
    transition: color 0.2s;
}
.back-home:hover {
    color: #4169e1 !important;
}
</style>