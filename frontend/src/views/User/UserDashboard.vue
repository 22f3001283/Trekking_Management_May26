<template>
    <h1>User Dashboard</h1>
</template>

<script>
import axios from 'axios';

// export default{
// 	data(){
// 		return {
//             formdata: {
//                 "email" : "",
//                 "password" : ""
//             }
// 		}
// 	},
// 	methods:{
// 		async login(){
//             try {
//                 const resp=await axios.post("http://127.0.0.1:5000/login", this.formdata)
//                 console.log(resp);
//                 localStorage.setItem('token', resp.data.token)
//                 this.username=resp.data.username;
//                 if(resp.msg="successfully logged in")
//                     this.$router.push('/hello')
//             } catch (err) {
//                 alert(err.response?.data?.msg || "Login failed")
//             }
//         }
// 	}
// }
</script>