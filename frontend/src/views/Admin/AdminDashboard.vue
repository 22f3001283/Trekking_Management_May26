<template>

<AdminNavbar />
<div style="margin-top: 60px;">
    <h3>Pending Users</h3>
    <ul>
        <li v-for="user in pending_users" :key="user.user_id">
            <p>{{ user.username }} - {{ user.email }}</p>
            <button @click="changeUserStatus(user.user_id, 'active')" v-if="user.status != 'active'">Approve</button>
            <button @click="changeUserStatus(user.user_id, 'inactive')" v-if="user.status != 'inactive'">Reject</button>
            <button @click="changeUserStatus(user.user_id, 'blacklisted')" v-if="user.status != 'blacklisted'">Blacklist</button>
        </li>
    </ul>
</div>
</template>
<script>
import axios from 'axios';
import AdminNavbar from '../../components/AdminNavbar.vue';

export default {
    components: { AdminNavbar },
    data(){
        return{
            'pending_users':[]
        }
    },
    methods: {
        async fetchPendingUsers() {
            try {
                const token = localStorage.getItem('token')
                const response = await axios.get("http://127.0.0.1:5000/users/pending", {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                this.pending_users=response.data
                console.log(this.pending_users)
            } catch (error) {
                console.error('Error fetching pending users:', error)
                alert('Failed to fetch pending users: ' + (error.response?.data?.msg || error.message))
            }
        },
        async changeUserStatus(user_id, status) {
            const token = localStorage.getItem('token')
            const response=await axios.put(`http://127.0.0.1:5000/users/${user_id}`, { status }, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            alert(response.data.msg)
            this.fetchPendingUsers()
        },
        // async approveUser(user_id) {
        //     const token = localStorage.getItem('token')
        //     const response=await axios.put(`http://127.0.0.1:5000/users/${user_id}/approve`, {}, {
        //         headers: { 'Authorization': `Bearer ${token}` }
        //     })
        //     alert(response.data.msg)
        //     this.fetchPendingUsers()
        // },
        // async rejectUser(user_id) {
        //     const token = localStorage.getItem('token')
        //     const response=await axios.delete(`http://127.0.0.1:5000/users/${user_id}/reject`, {
        //         headers: { 'Authorization': `Bearer ${token}` }
        //     })
        //     alert(response.data.msg)
        //     this.fetchPendingUsers()
        // }
    },
    mounted(){
        this.fetchPendingUsers()
    }
}
</script>