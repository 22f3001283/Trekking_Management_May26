<template>
    <h1>Admin Dashboard</h1>

    <h3>Pending Users</h3>
    <ul>
        <li v-for="user in pending_users" :key="user.user_id">
            <p>{{ user.username }} - {{ user.email }}</p>
            <button @click="approveUser(user.user_id)">Approve</button>
            <button @click="rejectUser(user.user_id)">Reject</button>
        </li>
    </ul>
</template>

<script>
import axios from 'axios';

export default {
    data(){
        return{
            'pending_users':[]
        }
    },
    methods: {
        async fetchPendingUsers() {
            const token = localStorage.getItem('token')
            const response = await axios.get("http://127.0.0.1:5000/users/pending", {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            this.pending_users=response.data
            console.log(this.pending_users)
        },
        async approveUser(user_id) {
            const token = localStorage.getItem('token')
            const response=await axios.put(`http://127.0.0.1:5000/users/${user_id}/approve`, {}, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            alert(response.data.msg)
            this.fetchPendingUsers()
        },
        async rejectUser(user_id) {
            const token = localStorage.getItem('token')
            const response=await axios.delete(`http://127.0.0.1:5000/users/${user_id}/reject`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            alert(response.data.msg)
            this.fetchPendingUsers()
        }

    },
    mounted(){
        this.fetchPendingUsers()
    }
}
</script>