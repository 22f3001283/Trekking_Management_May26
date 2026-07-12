<template>
    <div class="page-wrapper">
        <AdminNavbar />

        <div class="container-fluid page-content" style="margin-top: 50px; padding: 24px 80px;">

            <!-- Page header -->
            <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
                <div>
                    <h2 class="fw-bold mb-1">User Management</h2>
                </div>
                <div class="d-flex gap-2 flex-wrap">
                    <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                        <div class="fs-5 fw-semibold">{{ regularUsers.length }}</div>
                        <div class="text-muted text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Total</div>
                    </div>
                    <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                        <div class="fs-5 fw-semibold text-success">{{ countByStatus('active') }}</div>
                        <div class="text-muted text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Active</div>
                    </div>
                    <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                        <div class="fs-5 fw-semibold text-danger">{{ countByStatus('blacklisted') }}</div>
                        <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Blacklisted</div>
                    </div>
                </div>
            </div>

            <!-- Toolbar -->
            <div class="d-flex flex-wrap gap-2 align-items-center justify-content-end mb-3">
                <div class="input-group" style="max-width: 320px;">
                    <input v-model="searchQuery" type="text" class="form-control" :placeholder="'Search by ' + searchField">
                    <select class="form-select" v-model="searchField" style="max-width: 130px;">
                        <option value="username">Username</option>
                        <option value="email">Email</option>
                        <option value="contact">Contact</option>
                    </select>
                    <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="searchQuery = ''">Clear</button>
                </div>
                <select v-model="filterStatus" class="form-select form-select-sm w-auto">
                    <option value="">All statuses</option>
                    <option value="active">Active</option>
                    <option value="blacklisted">Blacklisted</option>
                </select>
                <select v-model="sortBy" class="form-select form-select-sm w-auto">
                    <option value="">Sort: none</option>
                    <option value="username_asc">Username: A–Z</option>
                    <option value="username_desc">Username: Z–A</option>
                    <option value="created_asc">Joined: oldest</option>
                    <option value="created_desc">Joined: newest</option>
                </select>
                <button class="btn btn-outline-primary btn-sm" @click="fetchUsers" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                    <span v-else>Refresh</span>
                </button>
            </div>

            <!-- Error -->
            <div v-if="error" class="alert alert-danger">{{ error }}</div>

            <!-- Loading -->
            <div v-if="loading" class="card shadow-sm p-3 border-0">
                <div v-for="n in 5" :key="n" class="placeholder-glow mb-2">
                    <span class="placeholder col-12 rounded" style="height: 38px; display: block;"></span>
                </div>
            </div>

            <!-- Empty -->
            <div v-else-if="filteredUsers.length === 0" class="alert alert-light border text-center py-5">
                <p class="mb-3 text-muted">No users match your filters.</p>
                <button class="btn btn-sm btn-outline-secondary" @click="resetFilters">Clear filters</button>
            </div>

            <!-- Table -->
            <div v-else class="card shadow-sm border-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="sortable" @click="setSortBy('username_asc', 'username_desc')">Username <span class="text-muted small">{{ sortArrow('username') }}</span></th>
                                <th>Email</th>
                                <th>Contact</th>
                                <th class="sortable" @click="setSortBy('created_asc', 'created_desc')">Joined <span class="text-muted small">{{ sortArrow('created') }}</span></th>
                                <th>Status</th>
                                <th style="width: 170px;">Update status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in paginated" :key="user.user_id">
                                <td class="fw-semibold text-primary">{{ user.username }}</td>
                                <td class="text-muted small">{{ user.email }}</td>
                                <td class="text-muted small">{{ user.contact || '—' }}</td>
                                <td class="text-muted small">{{ formatDate(user.created_at) }}</td>
                                <td><span class="fw-semibold" :class="statusTextClass(user.status)">{{ user.status }}</span></td>
                                <td @click.stop>
                                    <select class="form-select form-select-sm" :value="user.status" @change="handleStatusChange(user, $event.target.value)">
                                        <option value="active">Active</option>
                                        <option value="blacklisted">Blacklisted</option>
                                    </select>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pagination -->
            <nav v-if="totalPages > 1" class="d-flex justify-content-center mt-3">
                <ul class="pagination pagination-sm mb-0">
                    <li class="page-item" :class="{ disabled: page === 1 }">
                        <button class="page-link" @click="page--">Prev</button>
                    </li>
                    <li class="page-item disabled">
                        <span class="page-link border-0 bg-transparent text-muted">Page {{ page }} of {{ totalPages }}</span>
                    </li>
                    <li class="page-item" :class="{ disabled: page === totalPages }">
                        <button class="page-link" @click="page++">Next</button>
                    </li>
                </ul>
            </nav>

        </div>

        <footer class="bg-light text-center py-3 small mt-auto">
            © 2026 Trekking Management. All rights reserved.
        </footer>
    </div>
</template>

<script>
import axios from 'axios'
import AdminNavbar from '../../components/AdminNavbar.vue'

export default {
    components: { AdminNavbar },
    data() {
        return {
            users: [],
            loading: false,
            error: '',
            searchQuery: '',
            searchField: 'username',
            sortBy: '',
            filterStatus: '',
            page: 1,
            perPage: 10,
        }
    },
    computed: {
        regularUsers() {
            return this.users.filter(u => u.role === 'user')
        },
        filteredUsers() {
            let result = this.regularUsers

            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase()
                result = result.filter(u => {
                    const val = u[this.searchField]
                    return val ? val.toString().toLowerCase().includes(q) : false
                })
            }

            if (this.filterStatus) {
                result = result.filter(u => u.status === this.filterStatus)
            }

            if (this.sortBy === 'username_asc') result = [...result].sort((a, b) => a.username.localeCompare(b.username))
            else if (this.sortBy === 'username_desc') result = [...result].sort((a, b) => b.username.localeCompare(a.username))
            else if (this.sortBy === 'created_asc') result = [...result].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            else if (this.sortBy === 'created_desc') result = [...result].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

            return result
        },
        paginated() {
            const start = (this.page - 1) * this.perPage
            return this.filteredUsers.slice(start, start + this.perPage)
        },
        totalPages() {
            return Math.ceil(this.filteredUsers.length / this.perPage) || 1
        }
    },
    methods: {
        authHeader() {
            return { Authorization: `Bearer ${localStorage.getItem('token')}` }
        },
        async fetchUsers() {
            this.loading = true
            this.error = ''
            try {
                const response = await axios.get('http://127.0.0.1:5000/users', { headers: this.authHeader() })
                this.users = response.data
            } catch (e) {
                this.error = e.response?.data?.msg || 'Failed to load users.'
            } finally {
                this.loading = false
            }
        },
        async handleStatusChange(user, newStatus) {
            if (!confirm(`Set ${user.username}'s status to "${newStatus}"?`)) return
            try {
                const response = await axios.put(`http://127.0.0.1:5000/users/${user.user_id}`, { status: newStatus }, { headers: this.authHeader() })
                alert(response.data.msg)
                await this.fetchUsers()
            } catch (e) {
                alert(e.response?.data?.msg || 'Failed to update status')
            }
        },
        resetFilters() {
            this.searchQuery = ''
            this.searchField = 'username'
            this.sortBy = ''
            this.filterStatus = ''
            this.page = 1
        },
        countByStatus(status) {
            return this.regularUsers.filter(u => u.status === status).length
        },
        formatDate(dateStr) {
            if (!dateStr) return '—'
            return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
        },
        statusTextClass(status) {
            return {
                active: 'text-success',
                blacklisted: 'text-danger',
            }[status] || 'text-body'
        },
        setSortBy(asc, desc) {
            if (this.sortBy === asc) this.sortBy = desc
            else this.sortBy = asc
            this.page = 1
        },
        sortArrow(field) {
            if (this.sortBy === `${field}_asc`) return '↑'
            if (this.sortBy === `${field}_desc`) return '↓'
            return ''
        }
    },
    watch: {
        searchQuery() { this.page = 1 },
        filterStatus() { this.page = 1 },
        sortBy()       { this.page = 1 },
    },
    mounted() {
        this.fetchUsers()
    }
}
</script>

<style scoped>
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #4169e1; }

.page-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
.page-content {
    flex: 1;
}
</style>