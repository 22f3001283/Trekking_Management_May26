<template>
    <AdminNavbar v-if="role === 'admin'" />
    <StaffNavbar v-else-if="role === 'staff'" />
    <UserNavbar v-else-if="role === 'user'" />

    <div class="container-fluid" style="margin-top: 50px; padding: 24px 80px;">

        <!-- Back link, its own row above everything -->
        <button v-if="backPath" class="btn  btn-light mb-3dropdown-toggle" type="button" @click="$router.push(backPath)" style="margin-bottom: 10px;">
          <i class="bi bi-arrow-left"></i>  Back to dashboard
        </button>

        <!-- Page header -->
        <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
            <div>
                <h2 class="fw-bold mb-1">{{ pageTitle }}</h2>
                <p class="text-muted small mb-0">{{ pageSub }}</p>
            </div>
            <div class="d-flex gap-2 flex-wrap">
                <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                    <div class="fs-5 fw-semibold">{{ trekScopedBookings.length }}</div>
                    <div class="text-muted text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Total</div>
                </div>
                <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                    <div class="fs-5 fw-semibold text-primary">{{ countByStatus('Booked') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Active</div>
                </div>
                <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                    <div class="fs-5 fw-semibold text-danger">{{ countByStatus('Cancelled') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Cancelled</div>
                </div>
                <div class="border rounded-2 text-center px-3 py-2 bg-white" style="min-width: 74px;">
                    <div class="fs-5 fw-semibold text-success">{{ countByStatus('Completed') }}</div>
                    <div class="text-uppercase" style="font-size: 0.65rem; letter-spacing: .05em;">Completed</div>
                </div>
            </div>
        </div>

        <!-- Toolbar -->
        <div class="d-flex flex-wrap gap-2 align-items-center justify-content-end mb-3">
            <div class="input-group" style="max-width: 320px;">
                <input v-model="search" type="text" class="form-control" placeholder="Search by booking ID, user, trek">
                <button v-if="search" class="btn btn-outline-secondary" type="button" @click="search = ''">Clear</button>
            </div>
            <select v-model="filterStatus" class="form-select form-select-sm w-auto">
                <option value="">All statuses</option>
                <option value="Booked">Booked</option>
                <option value="Cancelled">Cancelled</option>
                <option value="Completed">Completed</option>
            </select>
            <select v-model="filterPayment" class="form-select form-select-sm w-auto">
                <option value="">All payments</option>
                <option value="Pending">Pending</option>
                <option value="Paid">Paid</option>
                <option value="Refund">Refund</option>
            </select>
            <button v-if="role === 'staff' && $route.query.trek_id" class="btn btn-outline-primary btn-sm" @click="openExportParticipantsModal">
                Export participants
            </button>
            <button class="btn btn-outline-primary btn-sm" @click="fetchBookings" :disabled="loading">
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
        <div v-else-if="filtered.length === 0" class="alert alert-light border text-center py-5">
            <p class="mb-3 text-muted">No bookings match your filters.</p>
            <button class="btn btn-sm btn-outline-secondary" @click="clearFilters">Clear filters</button>
        </div>

        <!-- Table -->
        <div v-else class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="sortable" @click="sortBy('booking_id')">ID <span class="text-muted small">{{ sortArrow('booking_id') }}</span></th>
                            <th class="sortable" @click="sortBy('user_id')">User <span class="text-muted small">{{ sortArrow('user_id') }}</span></th>
                            <th class="sortable" @click="sortBy('trek_id')">Trek <span class="text-muted small">{{ sortArrow('trek_id') }}</span></th>
                            <th class="sortable" @click="sortBy('booking_date')">Booked on <span class="text-muted small">{{ sortArrow('booking_date') }}</span></th>
                            <th>Participants</th>
                            <th>Booking status</th>
                            <th>Payment</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in paginated" :key="b.booking_id" style="cursor: pointer;" @click="openDetail(b)">
                            <td class="fw-semibold text-primary">#{{ b.booking_id }}</td>
                            <td class="fw-semibold">{{ getUserName(b.user_id) }}</td>
                            <td class="fw-semibold">{{ getTrekName(b.trek_id) }}</td>
                            <td class="text-muted small">{{ formatDate(b.booking_date) }}</td>
                            <td class="text-muted">{{ b.num_people }}</td>
                            <td class="fw-semibold" :class="statusTextClass(b.status)">{{ b.status }}</td>
                            <td class="fw-semibold" :class="paymentTextClass(b.payment_status)">{{ b.payment_status }}</td>
                            <td @click.stop>
                                <button class="btn btn-outline-primary btn-sm me-1" @click="openDetail(b)">View</button>
                                <button v-if="b.status === 'Booked' && canCancel(b)" class="btn btn-outline-danger btn-sm" @click="cancelBooking(b)">Cancel</button>
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
                <li class="page-item disabled"><span class="page-link border-0 bg-transparent text-muted">Page {{ page }} of {{ totalPages }}</span></li>
                <li class="page-item" :class="{ disabled: page === totalPages }">
                    <button class="page-link" @click="page++">Next</button>
                </li>
            </ul>
        </nav>

        <!-- Detail Modal -->
        <div class="modal fade" id="bookingDetailModal" tabindex="-1" aria-labelledby="bookingDetailModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content" v-if="selectedBooking">
                    <div class="modal-header">
                        <div>
                            <h5 class="modal-title" id="bookingDetailModalLabel">Booking #{{ selectedBooking.booking_id }}</h5>
                            <span class="fw-semibold" :class="statusTextClass(selectedBooking.status)">{{ selectedBooking.status }}</span>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row g-3 mb-3">
                            <div class="col-6 col-md-4">
                                <div class="text-muted text-uppercase small">User</div>
                                <div class="fw-semibold">{{ getUserName(selectedBooking.user_id) }} <span class="text-muted small">#{{ selectedBooking.user_id }}</span></div>
                            </div>
                            <div class="col-6 col-md-4">
                                <div class="text-muted text-uppercase small">Trek</div>
                                <div class="fw-semibold">{{ getTrekName(selectedBooking.trek_id) }} <span class="text-muted small">#{{ selectedBooking.trek_id }}</span></div>
                            </div>
                            <div class="col-6 col-md-4">
                                <div class="text-muted text-uppercase small">Booked on</div>
                                <div class="fw-semibold">{{ formatDate(selectedBooking.booking_date) }}</div>
                            </div>
                            <div class="col-6 col-md-4">
                                <div class="text-muted text-uppercase small">Participants</div>
                                <div class="fw-semibold">{{ selectedBooking.num_people }}</div>
                            </div>
                            <div class="col-6 col-md-4">
                                <div class="text-muted text-uppercase small">Payment</div>
                                <div class="fw-semibold" :class="paymentTextClass(selectedBooking.payment_status)">{{ selectedBooking.payment_status }}</div>
                            </div>
                        </div>

                        <h6 class="text-uppercase small fw-bold mb-2 text-primary">Participants</h6>
                        <div v-if="detailLoading" class="text-center py-3">
                            <span class="spinner-border spinner-border-sm"></span> Loading
                        </div>
                        <p v-else-if="detailParticipants.length === 0" class="text-muted small">No participant records found.</p>
                        <div v-else class="table-responsive">
                            <table class="table table-sm">
                                <thead class="table-light">
                                    <tr><th>#</th><th>Name</th><th>Date of birth</th><th>Aadhar</th></tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(p, i) in detailParticipants" :key="p.participant_id">
                                        <td>{{ i + 1 }}</td>
                                        <td>{{ p.name }}</td>
                                        <td>{{ p.dob }}</td>
                                        <td class="font-monospace text-muted">{{ maskAadhar(p.aadhar) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button v-if="selectedBooking.status === 'Booked' && canCancel(selectedBooking)" class="btn btn-outline-danger btn-sm" @click="cancelBooking(selectedBooking)">Cancel booking</button>
                        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Export Participants Modal -->
        <div class="modal fade" id="exportParticipantsModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Export participants</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">Include cancelled bookings in the participant list?</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal" @click="confirmExportParticipants(false)">Exclude cancelled</button>
                        <button class="btn btn-primary btn-sm" data-bs-dismiss="modal" @click="confirmExportParticipants(true)">Include cancelled</button>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import axios from 'axios'
import AdminNavbar from './AdminNavbar.vue';
import UserNavbar from './UserNavbar.vue';
import StaffNavbar from './StaffNavbar.vue'; 

export default {
  name: 'BookingHistory',
  components: { AdminNavbar, UserNavbar, StaffNavbar },
  data() {
    return {
      bookings: [],
      users: [],
      treks: [],
      role: localStorage.getItem('role'),
      currentUserId: parseInt(localStorage.getItem('user_id')),      
      loading: false,
      error: '',

      search: '',
      filterStatus: '',
      filterPayment: '',

      sortKey: 'booking_id',
      sortDir: -1,

      page: 1,
      perPage: 10,

      selectedBooking: null,
      detailParticipants: [],
      detailLoading: false,
    }
  },

  computed: {
    trekScopedBookings() {
      const trekFilter = this.$route.query.trek_id
      return trekFilter
        ? this.bookings.filter(b => String(b.trek_id) === String(trekFilter))
        : this.bookings
    },
    filtered() {
      const q = this.search.toLowerCase()
      return this.trekScopedBookings
        .filter(b => {
          const matchSearch =
            !q ||
            String(b.booking_id).includes(q) ||
            String(b.user_id).includes(q) ||
            this.getUserName(b.user_id).toLowerCase().includes(q) ||
            this.getTrekName(b.trek_id).toLowerCase().includes(q)

          const matchStatus  = !this.filterStatus  || b.status === this.filterStatus
          const matchPayment = !this.filterPayment || b.payment_status === this.filterPayment

          return matchSearch && matchStatus && matchPayment
        })
        .sort((a, b) => {
          const av = a[this.sortKey]
          const bv = b[this.sortKey]
          if (av < bv) return -this.sortDir
          if (av > bv) return  this.sortDir
          return 0
        })
    },

    totalPages() {
      return Math.ceil(this.filtered.length / this.perPage) || 1
    },

    paginated() {
      const start = (this.page - 1) * this.perPage
      return this.filtered.slice(start, start + this.perPage)
    },

    pageTitle() {
      if (this.role === 'admin') return 'All Bookings'
      if (this.role === 'staff') {
        const trekFilter = this.$route.query.trek_id
        const trek = trekFilter ? this.treks.find(t => String(t.trek_id) === String(trekFilter)) : null
        return trek ? `Bookings for ${trek.trek_name}` : 'Bookings for Your Treks'
      }
      return 'My Bookings History'
    },

    pageSub() {
      if (this.role === 'admin') return 'Complete booking history across every trek'
      if (this.role === 'staff') return 'Bookings made for treks assigned to you'
      return 'Your trek booking history'
    },

    backPath() {
      if (this.role === 'staff') return `/staff/${this.currentUserId}`
      if (this.role === 'user') return `/user/${this.currentUserId}`
      return null
    },
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: `Bearer ${token}` }
    },

    async fetchBookings() {
      this.loading = true
      this.error   = ''
      const userPromise = this.role === 'user' ? Promise.resolve({ data: [] }) : axios.get(`http://127.0.0.1:5000/users`, { headers: this.authHeader() })
        try {
        const [bRes, uRes, tRes] = await Promise.all([
          axios.get(`http://127.0.0.1:5000/bookings`,  { headers: this.authHeader() }),
          userPromise,
          axios.get(`http://127.0.0.1:5000/treks`,     { headers: this.authHeader() }),
        ])
        this.bookings = bRes.data
        this.users    = uRes.data
        this.treks    = tRes.data
      } catch (e) {
        this.error = e.response?.data?.msg || 'Failed to load bookings.'
      } finally {
        this.loading = false
      }
    },

    async openDetail(booking) {
      this.selectedBooking   = booking
      this.detailParticipants = []
      this.detailLoading      = true

      const modalEl = document.getElementById('bookingDetailModal')
      bootstrap.Modal.getOrCreateInstance(modalEl).show()

      try {
        const res = await axios.get(`http://127.0.0.1:5000/bookings/${booking.booking_id}`, {
          headers: this.authHeader()
        })
        this.detailParticipants = res.data.participants || []
      } catch {
        this.detailParticipants = []
      } finally {
        this.detailLoading = false
      }
    },

    async cancelBooking(booking) {
      if (!confirm(`Cancel Booking #${booking.booking_id}? This will restore trek slots.`)) return
      try {
        await axios.delete(`http://127.0.0.1:5000/bookings/${booking.booking_id}`, {
          headers: this.authHeader()
        })
        const modalEl = document.getElementById('bookingDetailModal')
        const modalInstance = bootstrap.Modal.getInstance(modalEl)
        if (modalInstance) modalInstance.hide()
        await this.fetchBookings()
      } catch (e) {
        alert(e.response?.data?.msg || 'Failed to cancel booking.')
      }
    },

    canCancel(booking) {
      return this.role === 'admin' || (this.role === 'user' && booking.user_id === this.currentUserId)
    },

    getUserName(userId) {
      if (this.role === 'user') return 'You'
      const u = this.users.find(u => u.user_id === userId)
      return u ? u.username : `User #${userId}`
    },

    getTrekName(trekId) {
      const t = this.treks.find(t => t.trek_id === trekId)
      return t ? t.trek_name : `Trek #${trekId}`
    },

    countByStatus(status) {
      return this.trekScopedBookings.filter(b => b.status === status).length
    },

    formatDate(iso) {
    if (!iso) return '—'
    return new Date(iso).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    })
    },

    maskAadhar(aadhar) {
      if (!aadhar || aadhar.length < 4) return aadhar
      return 'XXXX XXXX ' + aadhar.slice(-4)
    },

    statusTextClass(status) {
      return {
        'Booked':    'text-primary',
        'Cancelled': 'text-danger',
        'Completed': 'text-success',
      }[status] || 'text-dark'
    },

    paymentTextClass(status) {
      return {
        'Pending': 'text-primary',
        'Paid':    'text-success',
        'Refund':  'text-danger',
      }[status] || 'text-dark'
    },

    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDir *= -1
      } else {
        this.sortKey = key
        this.sortDir = -1
      }
      this.page = 1
    },

    sortArrow(key) {
      if (this.sortKey !== key) return ''
      return this.sortDir === -1 ? '↓' : '↑'
    },

    clearFilters() {
      this.search        = ''
      this.filterStatus  = ''
      this.filterPayment = ''
      this.page          = 1
    },

    openExportParticipantsModal() {
      const modalEl = document.getElementById('exportParticipantsModal')
      bootstrap.Modal.getOrCreateInstance(modalEl).show()
    },

    async confirmExportParticipants(includeCancelled) {
      const trekId = this.$route.query.trek_id
      if (!trekId) return
      try {
        const res = await axios.post(
          `http://127.0.0.1:5000/export/trek-participants/${trekId}`,
          { include_cancelled: includeCancelled },
          { headers: this.authHeader() }
        )
        this.pollExportStatus(res.data.task_id)
      } catch (e) {
        alert(e.response?.data?.msg || 'Failed to start export.')
      }
    },

    pollExportStatus(taskId) {
      const interval = setInterval(async () => {
        try {
          const res = await axios.get(`http://127.0.0.1:5000/export/status/${taskId}`, { headers: this.authHeader() })
          if (res.data.status === 'SUCCESS') {
            clearInterval(interval)
            this.downloadExportedFile(res.data.filename)
          } else if (res.data.status === 'FAILURE') {
            clearInterval(interval)
            alert('Export failed. Please try again.')
          }
        } catch (e) {
          clearInterval(interval)
          alert('Error checking export status.')
        }
      }, 2000)
    },

    async downloadExportedFile(filename) {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/export/download/${filename}`, {
          headers: this.authHeader(),
          responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        alert('Participant list downloaded successfully!')
      } catch (e) {
        alert('Failed to download file.')
      }
    },
  },

  mounted() {
    this.fetchBookings()
    const modalEl = document.getElementById('bookingDetailModal')
    if (modalEl) {
      modalEl.addEventListener('hidden.bs.modal', () => {
        this.selectedBooking = null
        this.detailParticipants = []
      })
    }
  },

  watch: {
    search()        { this.page = 1 },
    filterStatus()  { this.page = 1 },
    filterPayment() { this.page = 1 },
  },
}
</script>

<style scoped>
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #4169e1; }
</style>