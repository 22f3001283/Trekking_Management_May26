<template>
    <h1>Login</h1>
    <form>
        <label for="email"> Email </label>
        <input id="email" v-model="formdata.email" type="text">

        <label for="password"> Password </label>
        <input id="password" v-model="formdata.password" type="text">

        <button @click.prevent="login()"> Submit </button>
    </form>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            formdata: {
                "email": "",
                "password": ""
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