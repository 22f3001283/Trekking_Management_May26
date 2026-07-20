<template>
    <div class="page-wrapper">
        <AdminNavbar />

        <div class="container-fluid page-content" style="margin-top: 50px; padding: 24px 80px;">

            <!-- Page header -->
            <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
                <div>
                    <h2 class="fw-bold mb-1">Staff Management</h2>
                </div>
                <div class="d-flex gap-2 flex-wrap">
                    <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                        <div class="fs-5 fw-semibold">{{ staffList.length }}</div>
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
                <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#staffModal" @click="resetNewStaffForm">
                    Add staff
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
            <div v-else-if="filteredStaff.length === 0" class="alert alert-light border text-center py-5">
                <p class="mb-3 text-muted">No staff members match your filters.</p>
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
                                <th>Assigned treks</th>
                                <th style="width: 170px;">Update status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="staff in paginated" :key="staff.user_id">
                                <td class="fw-semibold text-primary">{{ staff.username }}</td>
                                <td class="text-muted small">{{ staff.email }}</td>
                                <td class="text-muted small">{{ staff.contact || '—' }}</td>
                                <td class="text-muted small">{{ formatDate(staff.created_at) }}</td>
                                <td><span class="fw-semibold" :class="statusTextClass(staff.status)">{{ staff.status }}</span></td>
                                <td>
                                    <button class="btn btn-outline-primary btn-sm" @click="viewAssignedTreks(staff)">
                                        View treks
                                        <span class="badge rounded-pill text-bg-primary ms-1">{{ getAssignedTreks(staff.user_id).length }}</span>
                                    </button>
                                </td>
                                <td @click.stop>
                                    <select class="form-select form-select-sm" :value="staff.status" @change="handleStatusChange(staff, $event.target.value)">
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

            <!-- Add Staff Modal -->
            <div class="modal fade" id="staffModal" tabindex="-1" aria-labelledby="staffModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="staffModalLabel">Add staff member</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" ref="closeModalBtn"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input class="form-control" v-model="newStaff.username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input class="form-control" type="email" v-model="newStaff.email" pattern="^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$" required>
                            </div>
                            <div class="mb-3">
                            <label class="form-label">Password</label>
                            <div class="input-group">
                                <input
                                class="form-control"
                                :class="{ 'is-invalid': staffPasswordError }"
                                :type="showStaffPassword ? 'text' : 'password'"
                                v-model="newStaff.password"
                                @input="validateStaffPassword"
                                required
                                >
                                <button
                                type="button"
                                class="input-group-text bg-white text-muted"
                                @click="showStaffPassword = !showStaffPassword"
                                :aria-label="showStaffPassword ? 'Hide password' : 'Show password'"
                                >
                                <svg v-if="!showStaffPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
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
                            <div v-if="staffPasswordError" class="text-danger small mt-1">{{ staffPasswordError }}</div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Contact</label>
                                <input class="form-control" v-model="newStaff.contact">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
                            <button class="btn btn-primary btn-sm" @click="handleAddStaff">Create staff</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="assignedTreksModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <div>
                                <h5 class="modal-title fw-bold">Assigned treks</h5>
                                <p class="text-muted small mb-0">{{ selectedStaffName }}</p>
                            </div>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body p-0">
                            <p v-if="selectedStaffTreks.length === 0" class="text-muted text-center py-4 mb-0">
                                No treks assigned yet.
                            </p>
                            <div v-else class="table-responsive">
                                <table class="table table-hover align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>ID</th>
                                            <th>Trek name</th>
                                            <th>Status</th>
                                            <th>Slots</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="trek in selectedStaffTreks" :key="trek.trek_id">
                                            <td class="fw-semibold text-primary">#{{ trek.trek_id }}</td>
                                            <td class="fw-semibold">{{ trek.trek_name }}</td>
                                            <td>
                                                <span class="fw-semibold" :class="trekStatusTextClass(trek.status)">
                                                    {{ trek.status }}
                                                </span>
                                            </td>
                                            <td class="text-muted small">{{ trek.available_slots ?? '—' }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>

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
        treks: [],
        loading: false,
        error: '',
        searchQuery: '',
        searchField: 'username',
        sortBy: '',
        filterStatus: '',
        page: 1,
        perPage: 10,
        newStaff: { username: '', email: '', password: '', contact: '' },
        staffPasswordError: '',    
        showStaffPassword: false,
        selectedStaffTreks: [],
        selectedStaffName: '',
    }
    },
    computed: {
        passwordRegex() {
            return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,20}$/
        },
        staffList() {
            return this.users.filter(u => u.role === 'staff')
        },
        filteredStaff() {
            let result = this.staffList

            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase()
                result = result.filter(s => {
                    const val = s[this.searchField]
                    return val ? val.toString().toLowerCase().includes(q) : false
                })
            }

            if (this.filterStatus) {
                result = result.filter(s => s.status === this.filterStatus)
            }

            if (this.sortBy === 'username_asc') result = [...result].sort((a, b) => a.username.localeCompare(b.username))
            else if (this.sortBy === 'username_desc') result = [...result].sort((a, b) => b.username.localeCompare(a.username))
            else if (this.sortBy === 'created_asc') result = [...result].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            else if (this.sortBy === 'created_desc') result = [...result].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

            return result
        },
        paginated() {
            const start = (this.page - 1) * this.perPage
            return this.filteredStaff.slice(start, start + this.perPage)
        },
        totalPages() {
            return Math.ceil(this.filteredStaff.length / this.perPage) || 1
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
                const [uRes, tRes] = await Promise.all([
                    axios.get('http://127.0.0.1:5000/users', { headers: this.authHeader() }),
                    axios.get('http://127.0.0.1:5000/treks', { headers: this.authHeader() }),
                ])
                this.users = uRes.data
                this.treks = tRes.data
            } catch (e) {
                this.error = e.response?.data?.msg || 'Failed to load staff.'
            } finally {
                this.loading = false
            }
        },
        resetNewStaffForm() {
            this.newStaff = { username: '', email: '', password: '', contact: '' }
            this.staffPasswordError = ''
            this.showStaffPassword = false
        },
        getAssignedTreks(staffId) {
            return this.treks.filter(t => t.assigned_staff_id === staffId)
        },
        viewAssignedTreks(staff) {
            this.selectedStaffName = staff.username
            this.selectedStaffTreks = this.getAssignedTreks(staff.user_id)
            bootstrap.Modal.getOrCreateInstance(document.getElementById('assignedTreksModal')).show()
        },
        trekStatusTextClass(status) {
            return {
                'Open': 'text-primary',
                'Approved': 'text-success',
                'Pending': 'text-secondary',
                'Closed': 'text-secondary',
                'Completed': 'text-success',
                'Cancelled': 'text-danger',
            }[status] || 'text-body'
        },
        validateStaffPassword() {
            const pwd = this.newStaff.password
            if (!pwd) {
            this.staffPasswordError = 'Password is required'
            return false
            }
            if (pwd.length < 8 || pwd.length > 20) {
            this.staffPasswordError = 'Password must be 8–20 characters long'
            return false
            }
            if (!this.passwordRegex.test(pwd)) {
            this.staffPasswordError = 'Must include uppercase, lowercase, a digit, and a special character'
            return false
            }
            this.staffPasswordError = ''
            return true
        },        
        async handleAddStaff() {
            if (!this.validateStaffPassword()) {  
                return
            }
            const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

            if (!emailRegex.test(this.newStaff.email)) {
                alert("Please enter a valid email address.");
                return;
            }
            try {
                const response = await axios.post('http://127.0.0.1:5000/staff', this.newStaff, { headers: this.authHeader() })
                alert(response.data.msg)
                this.resetNewStaffForm()
                await this.fetchUsers()
                this.$refs.closeModalBtn.click()
            } catch (e) {
                alert(e.response?.data?.msg || 'Failed to create staff member')
            }
        },
        async handleStatusChange(staff, newStatus) {
            if (!confirm(`Set ${staff.username}'s status to "${newStatus}"?`)) return
            try {
                const response = await axios.put(`http://127.0.0.1:5000/users/${staff.user_id}`, { status: newStatus }, { headers: this.authHeader() })
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
            return this.staffList.filter(s => s.status === status).length
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
        },
    },
    watch: {
        searchQuery() { this.page = 1 },
        filterStatus() { this.page = 1 },
        sortBy()       { this.page = 1 },
    },
    mounted() {
        this.fetchUsers()
        const treksModalEl = document.getElementById('assignedTreksModal')
        if (treksModalEl) {
            treksModalEl.addEventListener('hidden.bs.modal', () => {
                this.selectedStaffTreks = []
                this.selectedStaffName = ''
            })
        }
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