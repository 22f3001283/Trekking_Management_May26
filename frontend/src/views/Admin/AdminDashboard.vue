<template>
    <AdminNavbar />

    <div class="container-fluid" style="margin-top: 50px; padding: 24px 80px; background-color: #f6f5fb; min-height: 100vh;">

        <!-- Page header -->
        <div class="mb-4">
            <h2 class="fw-bold mb-1">Admin Dashboard</h2>
            <p class="text-muted small mb-0">Overview of your platform at a glance</p>
        </div>

        <!-- Stat Cards -->
        <div class="row g-3 mb-5">
            <div class="col-6 col-md-3">
                <div class="card border-0 shadow-sm h-100" style="border-left: 4px solid #9e52eb !important;">
                    <div class="card-body">
                        <div class="text-muted text-uppercase mb-1" style="font-size: 0.7rem; letter-spacing: .07em;">Total Treks</div>
                        <div class="fs-2 fw-bold" style="color: #9e52eb;">{{ stats.treks }}</div>
                        <div class="text-muted small mt-1">🏔️ across all statuses</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card border-0 shadow-sm h-100" style="border-left: 4px solid #198754 !important;">
                    <div class="card-body">
                        <div class="text-muted text-uppercase mb-1" style="font-size: 0.7rem; letter-spacing: .07em;">Total Users</div>
                        <div class="fs-2 fw-bold text-success">{{ stats.users }}</div>
                        <div class="text-muted small mt-1">🧑‍🤝‍🧑 registered accounts</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card border-0 shadow-sm h-100" style="border-left: 4px solid #0d6efd !important;">
                    <div class="card-body">
                        <div class="text-muted text-uppercase mb-1" style="font-size: 0.7rem; letter-spacing: .07em;">Total Staff</div>
                        <div class="fs-2 fw-bold text-primary">{{ stats.staff }}</div>
                        <div class="text-muted small mt-1">🧑‍✈️ active guides & crew</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card border-0 shadow-sm h-100" style="border-left: 4px solid #fd7e14 !important;">
                    <div class="card-body">
                        <div class="text-muted text-uppercase mb-1" style="font-size: 0.7rem; letter-spacing: .07em;">Total Bookings</div>
                        <div class="fs-2 fw-bold text-warning">{{ stats.bookings }}</div>
                        <div class="text-muted small mt-1">🎒 all time</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="alert alert-danger mb-4">{{ error }}</div>

        <!-- ── Pending Approvals ── -->
        <div class="mb-5">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-0">Pending Approvals</h5>
                    <p class="text-muted small mb-0">Newly registered accounts awaiting activation</p>
                </div>
                <button class="btn btn-sm text-white" style="background-color: #9e52eb;" @click="fetchAll" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                    <span v-else>↻ Refresh</span>
                </button>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="card shadow-sm border-0 p-3">
                <div v-for="n in 3" :key="n" class="placeholder-glow mb-2">
                    <span class="placeholder col-12 rounded" style="height: 38px; display: block;"></span>
                </div>
            </div>

            <!-- Empty -->
            <div v-else-if="pendingUsers.length === 0" class="alert alert-light border text-center py-4">
                <div class="fs-2 mb-1">✅</div>
                <p class="mb-0 text-muted">No pending approvals — you're all caught up!</p>
            </div>

            <!-- Table -->
            <div v-else class="card shadow-sm border-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="thead-purple">
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Contact</th>
                                <th>Type</th>
                                <th>Registered</th>
                                <th>Current Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in pendingUsers" :key="user.user_id">
                                <td class="fw-semibold" style="color: #9e52eb;">{{ user.username }}</td>
                                <td class="text-muted small">{{ user.email }}</td>
                                <td class="text-muted small">{{ user.contact || '—' }}</td>
                                <td>
                                    <span class="badge rounded-pill" :class="user.role === 'staff' ? 'bg-primary-subtle text-primary-emphasis' : 'bg-secondary-subtle text-secondary-emphasis'">
                                        {{ user.role === 'staff' ? '🧑‍✈️ Staff' : '🧑 User' }}
                                    </span>
                                </td>
                                <td class="text-muted small">{{ formatDate(user.created_at) }}</td>
                                <td>
                                    <span class="badge rounded-pill" :class="statusBadgeClass(user.status)">{{ user.status }}</span>
                                </td>
                                <td>
                                    <button v-if="user.status !== 'active'"
                                        class="btn btn-sm me-1"
                                        style="background-color: #e8f5e9; color: #2e7d32; border: none;"
                                        @click="changeUserStatus(user.user_id, 'active')">
                                        ✓ Approve
                                    </button>
                                    <button v-if="user.status !== 'blacklisted'"
                                        class="btn btn-sm"
                                        style="background-color: #fee2e2; color: #b91c1c; border: none;"
                                        @click="changeUserStatus(user.user_id, 'blacklisted')">
                                        ✕ Blacklist
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ── Pending Treks ── -->
        <div class="mb-4">
            <div class="mb-3">
                <h5 class="fw-bold mb-0">Pending Treks</h5>
                <p class="text-muted small mb-0">Treks with incomplete details — fill them in to mark Open or Approved</p>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="card shadow-sm border-0 p-3">
                <div v-for="n in 3" :key="n" class="placeholder-glow mb-2">
                    <span class="placeholder col-12 rounded" style="height: 38px; display: block;"></span>
                </div>
            </div>

            <!-- Empty -->
            <div v-else-if="pendingTreks.length === 0" class="alert alert-light border text-center py-4">
                <div class="fs-2 mb-1">🏔️</div>
                <p class="mb-0 text-muted">No pending treks — everything is up to date!</p>
            </div>

            <!-- Table -->
            <div v-else class="card shadow-sm border-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="thead-purple">
                            <tr>
                                <th># ID</th>
                                <th>Trek Name</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Duration</th>
                                <th>Price</th>
                                <th>Guide</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="trek in pendingTreks" :key="trek.trek_id">
                                <td class="fw-bold" style="color: #9e52eb;">#{{ trek.trek_id }}</td>
                                <td class="fw-semibold">{{ trek.trek_name }}</td>
                                <td class="text-muted small">
                                    <span v-if="trek.location">{{ trek.location }}</span>
                                    <span v-else class="badge rounded-pill bg-warning-subtle text-warning-emphasis">Missing</span>
                                </td>
                                <td>
                                    <span v-if="trek.difficulty" class="badge rounded-pill bg-light text-dark border">{{ trek.difficulty }}</span>
                                    <span v-else class="badge rounded-pill bg-warning-subtle text-warning-emphasis">Missing</span>
                                </td>
                                <td class="text-muted small">{{ trek.duration_days ? trek.duration_days + ' days' : '—' }}</td>
                                <td class="text-muted small">{{ trek.price ? '₹' + trek.price : '—' }}</td>
                                <td>
                                    <span v-if="trek.assigned_staff_name" class="badge rounded-pill" style="background-color: #ede9fb; color: #5b2ea0;">{{ trek.assigned_staff_name }}</span>
                                    <span v-else class="badge rounded-pill bg-warning-subtle text-warning-emphasis">Unassigned</span>
                                </td>
                                <td>
                                    <button class="btn btn-sm me-1 soft-btn" style="background-color: #ede9fb; color: #7c3fc2;"
                                        @click="handleViewClick(trek)"
                                        data-bs-toggle="modal" data-bs-target="#dashTrekModal">
                                        👁 View
                                    </button>
                                    <button class="btn btn-sm soft-btn" style="background-color: #fff3cd; color: #856404;"
                                        @click="handleEditClick(trek)"
                                        data-bs-toggle="modal" data-bs-target="#dashTrekModal">
                                        ✏️ Edit
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <!-- Trek Modal (same as AdminTrek.vue) -->
    <div class="modal fade" id="dashTrekModal" tabindex="-1" aria-labelledby="dashTrekModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="dashTrekModalLabel">
                        {{ currentMode === 'edit' ? '✏️ Edit Trek' : '👁 View Trek' }}
                        <span v-if="currentTrek" class="text-muted small fw-normal ms-2">#{{ currentTrek.trek_id }}</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <Trek
                        ref="trekFormRef"
                        :key="currentMode + (currentTrek?.trek_id || 'new')"
                        :mode="currentMode"
                        :trek="currentTrek"
                        @submit="handleTrekSubmit"
                        @cancel="handleCancel"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import AdminNavbar from '../../components/AdminNavbar.vue'
import Trek from '../../components/Trek.vue'

export default {
    name: 'AdminDashboard',
    components: { AdminNavbar, Trek },
    data() {
        return {
            allUsers: [],
            allTreks: [],
            allBookings: [],
            loading: false,
            error: '',
            currentMode: 'view',
            currentTrek: null,
        }
    },
    computed: {
        stats() {
            return {
                treks:    this.allTreks.length,
                users:    this.allUsers.filter(u => u.role === 'user').length,
                staff:    this.allUsers.filter(u => u.role === 'staff').length,
                bookings: this.allBookings.length,
            }
        },
        pendingUsers() {
            return this.allUsers.filter(u => u.status === 'inactive' || u.status === 'blacklisted')
        },
        pendingTreks() {
            return this.allTreks.filter(t => t.status === 'Pending')
        },
    },
    methods: {
        authHeader() {
            return { Authorization: `Bearer ${localStorage.getItem('token')}` }
        },
        async fetchAll() {
            this.loading = true
            this.error = ''
            try {
                const [uRes, tRes, bRes] = await Promise.all([
                    axios.get('http://127.0.0.1:5000/users',    { headers: this.authHeader() }),
                    axios.get('http://127.0.0.1:5000/treks',    { headers: this.authHeader() }),
                    axios.get('http://127.0.0.1:5000/bookings', { headers: this.authHeader() }),
                ])
                this.allUsers    = uRes.data
                this.allTreks    = tRes.data
                this.allBookings = bRes.data
            } catch (e) {
                this.error = e.response?.data?.msg || 'Failed to load dashboard data.'
            } finally {
                this.loading = false
            }
        },
        async changeUserStatus(user_id, status) {
            try {
                const response = await axios.put(
                    `http://127.0.0.1:5000/users/${user_id}`,
                    { status },
                    { headers: this.authHeader() }
                )
                alert(response.data.msg)
                await this.fetchAll()
            } catch (e) {
                alert(e.response?.data?.msg || 'Failed to update status.')
            }
        },
        handleViewClick(trek) {
            this.currentMode = 'view'
            this.currentTrek = trek
        },
        handleEditClick(trek) {
            this.currentMode = 'edit'
            this.currentTrek = trek
        },
        async handleTrekSubmit(formData) {
            if (!formData || formData.isTrusted !== undefined) return
            try {
                const response = await axios.put(
                    `http://127.0.0.1:5000/treks/${this.currentTrek.trek_id}`,
                    formData,
                    { headers: { ...this.authHeader(), 'Content-Type': 'application/json' } }
                )
                alert(response.data.msg)
                await this.fetchAll()
                this.$refs.trekFormRef.resetForm()
                bootstrap.Modal.getInstance(document.getElementById('dashTrekModal')).hide()
            } catch (e) {
                alert(e.response?.data?.msg || 'Failed to save trek.')
            }
        },
        handleCancel() {
            this.$refs.trekFormRef.resetForm()
            bootstrap.Modal.getInstance(document.getElementById('dashTrekModal')).hide()
        },
        formatDate(dateStr) {
            if (!dateStr) return '—'
            return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
        },
        statusBadgeClass(status) {
            return {
                active:      'bg-success-subtle text-success-emphasis',
                inactive:    'bg-warning-subtle text-warning-emphasis',
                blacklisted: 'bg-danger-subtle text-danger-emphasis',
            }[status] || 'bg-light text-dark'
        },
    },
    mounted() {
        this.fetchAll()
        const modalEl = document.getElementById('dashTrekModal')
        if (modalEl) {
            modalEl.addEventListener('hidden.bs.modal', () => {
                this.currentTrek = null
            })
        }
    },
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
.soft-btn { border: none; }
.soft-btn:hover { opacity: .8; }
</style>