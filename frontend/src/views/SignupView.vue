<template>
    <h1>Sign up</h1>

    <label for="username"> Username </label>
    <input id="username" v-model="username" type="text">	

    <label for="email"> email </label>
    <input id="email" v-model="email" type="text">

    <label for="password"> password </label>
    <input id="password" v-model="password" type="text">

    <button @click="signup()"> submit </button>

</template>


<script>
import axios from 'axios';

export default{
    data(){
        return {
            email: "",
            password: "",
			username: ""
        };
    },
    
    methods: {
        async signup(){
        try {
            const formdata = {
                email: this.email,
                password: this.password,
                username: this.username
            }
            const resp = await axios.post("http://127.0.0.1:5000/signup", formdata)
            if (resp.data.msg == "user created correctly") {
                alert("user created")
                this.$router.push({ name: 'login' })
            }
        } catch (err) {
            alert(err.response?.data?.msg || "Signup failed")
        }
        }
    }

}
</script>