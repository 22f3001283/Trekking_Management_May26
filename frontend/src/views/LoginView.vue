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

export default{
	data(){
		return {
            formdata: {
                "email" : "",
                "password" : ""
            }
		}
	},
	methods:{
		async login(){
            try {
                const resp=await axios.post("http://127.0.0.1:5000/login", this.formdata)
                console.log(resp);
                localStorage.setItem('token', resp.data.token)
                localStorage.setItem('token', resp.data.token)
                if(resp.data.role==="admin")
                    this.$router.push('/admin')
                else if(resp.data.role==="staff")
                    this.$router.push('/staff')
                else if(resp.data.role==="user")
                    this.$router.push('/user')
                else
                    this.$router.push('/')
            } catch (err) {
                alert(err.response?.data?.msg || "Login failed")
            }
        }
	}
}
</script>