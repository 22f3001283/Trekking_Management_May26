<template>
    <AdminNavbar />

    <div class="container-fluid" style="margin-top: 50px; padding: 24px 80px; background-color: #f6f5fb; min-height: 100vh;">

        <!-- Page header -->
        <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
            <div>
                <h2 class="fw-bold mb-1">User Management</h2>
                <p class="text-muted small mb-0">Review sign-ups and manage user access</p>
            </div>
            <div class="d-flex gap-2 flex-wrap">
                <div class="border rounded-3 text-center px-3 py-2 bg-white" style="min-width: 70px;">
                    <div class="fs-5 fw-bold">{{ regularUsers.length }}</div>
                    <div class="text-muted text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Total</div>
                </div>
                <div class="rounded-3 text-center px-3 py-2 border border-success bg-success-subtle" style="min-width: 70px;">
                    <div class="fs-5 fw-bold">{{ countByStatus('active') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Active</div>
                </div>
                <div class="rounded-3 text-center px-3 py-2 border border-secondary bg-secondary-subtle" style="min-width: 70px;">
                    <div class="fs-5 fw-bold">{{ countByStatus('inactive') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Inactive</div>
                </div>
                <div class="rounded-3 text-center px-3 py-2 border border-danger bg-danger-subtle" style="min-width: 70px;">
                    <div class="fs-5 fw-bold">{{ countByStatus('blacklisted') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Blacklisted</div>
                </div>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="d-flex flex-wrap gap-2 align-items-center justify-content-end mb-3">
            <div class="input-group" style="max-width: 320px;">
                <span class="input-group-text bg-white">🔍</span>
                <input v-model="searchQuery" type="text" class="form-control search-input-purple" :placeholder="'Search by ' + searchField + '…'">
                <select class="form-select" v-model="searchField" style="max-width: 130px;">
                    <option value="username">Username</option>
                    <option value="email">Email</option>
                    <option value="contact">Contact</option>
                </select>
                <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="searchQuery = ''">✕</button>
            </div>
            <select v-model="filterStatus" class="form-select form-select-sm w-auto">
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="blacklisted">Blacklisted</option>
            </select>
            <select v-model="sortBy" class="form-select form-select-sm w-auto">
                <option value="">Sort: None</option>
                <option value="username_asc">Username: A–Z</option>
                <option value="username_desc">Username: Z–A</option>
                <option value="created_asc">Joined: Oldest</option>
                <option value="created_desc">Joined: Newest</option>
            </select>
            <button class="btn btn-sm text-white" style="background-color: #9e52eb;" @click="fetchUsers" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>↻ Refresh</span>
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
            <div class="fs-1 mb-2">🧑‍🤝‍🧑</div>
            <p class="mb-3 text-muted">No users match your filters.</p>
            <button class="btn btn-sm btn-outline-secondary" @click="resetFilters">Clear filters</button>
        </div>

        <!-- Table -->
        <div v-else class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="thead-purple">
                        <tr>
                            <th class="sortable" @click="setSortBy('username_asc', 'username_desc')">Username <span class="opacity-50">{{ sortArrow('username') }}</span></th>
                            <th>Email</th>
                            <th>Contact</th>
                            <th class="sortable" @click="setSortBy('created_asc', 'created_desc')">Joined <span class="opacity-50">{{ sortArrow('created') }}</span></th>
                            <th>Status</th>
                            <th style="width: 170px;">Update Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in paginated" :key="user.user_id">
                            <td class="fw-semibold" style="color: #9e52eb;">{{ user.username }}</td>
                            <td class="text-muted small">{{ user.email }}</td>
                            <td class="text-muted small">{{ user.contact || '—' }}</td>
                            <td class="text-muted small">{{ formatDate(user.created_at) }}</td>
                            <td><span class="badge rounded-pill" :class="statusBadgeClass(user.status)">{{ user.status }}</span></td>
                            <td @click.stop>
                                <select class="form-select form-select-sm" :value="user.status" @change="handleStatusChange(user, $event.target.value)">
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
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
            <ul class="pagination pagination-purple mb-0">
                <li class="page-item" :class="{ disabled: page === 1 }">
                    <button class="page-link" @click="page--">‹ Prev</button>
                </li>
                <li class="page-item disabled">
                    <span class="page-link border-0 bg-transparent text-muted">Page {{ page }} of {{ totalPages }}</span>
                </li>
                <li class="page-item" :class="{ disabled: page === totalPages }">
                    <button class="page-link" @click="page++">Next ›</button>
                </li>
            </ul>
        </nav>

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
        statusBadgeClass(status) {
            return {
                active: 'bg-success-subtle text-success-emphasis',
                inactive: 'bg-secondary-subtle text-secondary-emphasis',
                blacklisted: 'bg-danger-subtle text-danger-emphasis',
            }[status] || 'bg-light text-dark'
        },
        setSortBy(asc, desc) {
            if (this.sortBy === asc) this.sortBy = desc
            else this.sortBy = asc
            this.page = 1
        },
        sortArrow(field) {
            if (this.sortBy === `${field}_asc`) return '↑'
            if (this.sortBy === `${field}_desc`) return '↓'
            return '↕'
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
.thead-purple th {
    background-color: #f3edff;
    color: #7c3fc2;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
}
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #5b2ea0; }
.search-input-purple:focus { border-color: #9e52eb; box-shadow: none; }
.pagination-purple .page-link { color: #7c3fc2; }
.pagination-purple .page-link:hover { border-color: #9e52eb; }
</style>