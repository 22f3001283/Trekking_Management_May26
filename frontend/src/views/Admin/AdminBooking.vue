<template>
    <AdminNavbar/>
    <div class="admin-bookings" style="margin-top: 40px;">

        <!-- ── Page header ── -->
        <div class="page-header">
        <div>
            <h2 class="page-title">All Bookings</h2>
            <p class="page-sub">Complete booking history across every trek</p>
        </div>
        <div class="header-stats">
            <div class="stat-chip">
            <span class="stat-num">{{ bookings.length }}</span>
            <span class="stat-label">Total</span>
            </div>
            <div class="stat-chip booked">
            <span class="stat-num">{{ countByStatus('Booked') }}</span>
            <span class="stat-label">Active</span>
            </div>
            <div class="stat-chip cancelled">
            <span class="stat-num">{{ countByStatus('Cancelled') }}</span>
            <span class="stat-label">Cancelled</span>
            </div>
            <div class="stat-chip completed">
            <span class="stat-num">{{ countByStatus('Completed') }}</span>
            <span class="stat-label">Completed</span>
            </div>
        </div>
        </div>

        <!-- ── Toolbar ── -->
        <div class="toolbar">
        <div class="search-wrap">
            <span class="search-icon">🔍</span>
            <input
            v-model="search"
            type="text"
            class="search-input"
            placeholder="Search by booking ID, user, trek…"
            />
            <button v-if="search" class="clear-btn" @click="search = ''">✕</button>
        </div>
        <div class="filter-group">
            <select v-model="filterStatus" class="filter-select">
            <option value="">All Statuses</option>
            <option value="Booked">Booked</option>
            <option value="Cancelled">Cancelled</option>
            <option value="Completed">Completed</option>
            </select>
            <select v-model="filterPayment" class="filter-select">
            <option value="">All Payments</option>
            <option value="Pending">Pending</option>
            <option value="Paid">Paid</option>
            <option value="Failed">Failed</option>
            </select>
            <button class="refresh-btn" @click="fetchBookings" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm"></span>
            <span v-else>↻ Refresh</span>
            </button>
        </div>
        </div>

        <!-- ── Error ── -->
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <!-- ── Loading skeleton ── -->
        <div v-if="loading" class="skeleton-wrap">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
        </div>

        <!-- ── Empty state ── -->
        <div v-else-if="filtered.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">🏔️</div>
        <p class="empty-msg">No bookings match your filters.</p>
        <button class="btn btn-sm btn-outline-secondary" @click="clearFilters">Clear filters</button>
        </div>

        <!-- ── Table ── -->
        <div v-else class="table-wrap">
        <table class="bookings-table">
            <thead>
            <tr>
                <th @click="sortBy('booking_id')" class="sortable">
                # ID <span class="sort-arrow">{{ sortArrow('booking_id') }}</span>
                </th>
                <th @click="sortBy('user_id')" class="sortable">
                User <span class="sort-arrow">{{ sortArrow('user_id') }}</span>
                </th>
                <th @click="sortBy('trek_id')" class="sortable">
                Trek <span class="sort-arrow">{{ sortArrow('trek_id') }}</span>
                </th>
                <th @click="sortBy('booking_date')" class="sortable">
                Booked On <span class="sort-arrow">{{ sortArrow('booking_date') }}</span>
                </th>
                <th>Participants</th>
                <th>Booking Status</th>
                <th>Payment</th>
                <th>Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr
                v-for="b in paginated"
                :key="b.booking_id"
                class="booking-row"
                @click="openDetail(b)"
            >
                <td><span class="booking-id">#{{ b.booking_id }}</span></td>
                <td>
                <span class="user-pill">{{ getUserName(b.user_id) }}</span>
                </td>
                <td>
                <span class="trek-name">{{ getTrekName(b.trek_id) }}</span>
                </td>
                <td class="date-cell">{{ formatDate(b.booking_date) }}</td>
                <td class="center-cell">
                <span class="people-badge">{{ b.num_people }} 👤</span>
                </td>
                <td>
                <span :class="['status-badge', statusClass(b.status)]">{{ b.status }}</span>
                </td>
                <td>
                <span :class="['payment-badge', paymentClass(b.payment_status)]">{{ b.payment_status }}</span>
                </td>
                <td @click.stop>
                <button class="action-btn view-btn" @click="openDetail(b)" title="View details">👁 View</button>
                <button
                    v-if="b.status === 'Booked'"
                    class="action-btn cancel-btn"
                    @click="cancelBooking(b)"
                    title="Cancel booking"
                >✕ Cancel</button>
                </td>
            </tr>
            </tbody>
        </table>
        </div>

        <!-- ── Pagination ── -->
        <div v-if="totalPages > 1" class="pagination-bar">
        <button class="page-btn" :disabled="page === 1" @click="page--">‹ Prev</button>
        <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
        <button class="page-btn" :disabled="page === totalPages" @click="page++">Next ›</button>
        </div>

        <!-- ── Detail Modal ── -->
        <div v-if="selectedBooking" class="modal-overlay" @click.self="closeDetail">
        <div class="modal-card">

            <div class="modal-header-bar">
            <div>
                <h5 class="modal-title-text">Booking #{{ selectedBooking.booking_id }}</h5>
                <span :class="['status-badge', statusClass(selectedBooking.status)]">
                {{ selectedBooking.status }}
                </span>
            </div>
            <button class="modal-close" @click="closeDetail">✕</button>
            </div>

            <div class="modal-body-grid">
            <div class="detail-block">
                <div class="detail-label">User</div>
                <div class="detail-value">{{ getUserName(selectedBooking.user_id) }} <span class="id-tag">#{{ selectedBooking.user_id }}</span></div>
            </div>
            <div class="detail-block">
                <div class="detail-label">Trek</div>
                <div class="detail-value">{{ getTrekName(selectedBooking.trek_id) }} <span class="id-tag">#{{ selectedBooking.trek_id }}</span></div>
            </div>
            <div class="detail-block">
                <div class="detail-label">Booked On</div>
                <div class="detail-value">{{ formatDate(selectedBooking.booking_date) }}</div>
            </div>
            <div class="detail-block">
                <div class="detail-label">Participants</div>
                <div class="detail-value">{{ selectedBooking.num_people }}</div>
            </div>
            <div class="detail-block">
                <div class="detail-label">Payment</div>
                <div class="detail-value">
                <span :class="['payment-badge', paymentClass(selectedBooking.payment_status)]">
                    {{ selectedBooking.payment_status }}
                </span>
                </div>
            </div>
            </div>

            <!-- Participants list -->
            <div class="participants-section">
            <div class="participants-heading">Participants</div>
            <div v-if="detailLoading" class="text-center py-3">
                <span class="spinner-border spinner-border-sm"></span> Loading…
            </div>
            <div v-else-if="detailParticipants.length === 0" class="no-participants">
                No participant records found.
            </div>
            <table v-else class="participants-table">
                <thead>
                <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Date of Birth</th>
                    <th>Aadhar</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(p, i) in detailParticipants" :key="p.participant_id">
                    <td>{{ i + 1 }}</td>
                    <td>{{ p.name }}</td>
                    <td>{{ p.dob }}</td>
                    <td class="aadhar-cell">{{ maskAadhar(p.aadhar) }}</td>
                </tr>
                </tbody>
            </table>
            </div>

            <div class="modal-footer-bar">
            <button
                v-if="selectedBooking.status === 'Booked'"
                class="btn btn-danger btn-sm"
                @click="cancelBooking(selectedBooking); closeDetail()"
            >Cancel Booking</button>
            <button class="btn btn-secondary btn-sm ms-2" @click="closeDetail">Close</button>
            </div>

        </div>
        </div>

    </div>
</template>

<script>
import axios from 'axios'
import AdminNavbar from '../../components/AdminNavbar.vue';

const BASE = 'http://127.0.0.1:5000'

export default {
  name: 'AdminBookings',
  components: { AdminNavbar },
  data() {
    return {
      bookings: [],
      users: [],
      treks: [],
      loading: false,
      error: '',

      search: '',
      filterStatus: '',
      filterPayment: '',

      sortKey: 'booking_id',
      sortDir: -1,   // -1 desc, 1 asc

      page: 1,
      perPage: 10,

      selectedBooking: null,
      detailParticipants: [],
      detailLoading: false,
    }
  },

  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.bookings
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
  },

  methods: {
    authHeader() {
      const token = localStorage.getItem('token')
      return { Authorization: `Bearer ${token}` }
    },

    async fetchBookings() {
      this.loading = true
      this.error   = ''
      try {
        const [bRes, uRes, tRes] = await Promise.all([
          axios.get(`${BASE}/bookings`,  { headers: this.authHeader() }),
          axios.get(`${BASE}/users`,     { headers: this.authHeader() }),
          axios.get(`${BASE}/treks`,     { headers: this.authHeader() }),
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
      try {
        const res = await axios.get(`${BASE}/bookings/${booking.booking_id}`, {
          headers: this.authHeader()
        })
        this.detailParticipants = res.data.participants || []
      } catch {
        this.detailParticipants = []
      } finally {
        this.detailLoading = false
      }
    },

    closeDetail() {
      this.selectedBooking    = null
      this.detailParticipants = []
    },

    async cancelBooking(booking) {
      if (!confirm(`Cancel Booking #${booking.booking_id}? This will restore trek slots.`)) return
      try {
        await axios.delete(`${BASE}/bookings/${booking.booking_id}`, {
          headers: this.authHeader()
        })
        await this.fetchBookings()
      } catch (e) {
        alert(e.response?.data?.msg || 'Failed to cancel booking.')
      }
    },

    getUserName(userId) {
      const u = this.users.find(u => u.user_id === userId)
      return u ? u.username : `User #${userId}`
    },

    getTrekName(trekId) {
      const t = this.treks.find(t => t.trek_id === trekId)
      return t ? t.trek_name : `Trek #${trekId}`
    },

    countByStatus(status) {
      return this.bookings.filter(b => b.status === status).length
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

    statusClass(status) {
      return {
        'Booked':    'status-booked',
        'Cancelled': 'status-cancelled',
        'Completed': 'status-completed',
      }[status] || ''
    },

    paymentClass(status) {
      return {
        'Paid':    'pay-paid',
        'Pending': 'pay-pending',
        'Failed':  'pay-failed',
      }[status] || ''
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
      if (this.sortKey !== key) return '↕'
      return this.sortDir === -1 ? '↓' : '↑'
    },

    clearFilters() {
      this.search        = ''
      this.filterStatus  = ''
      this.filterPayment = ''
      this.page          = 1
    },
  },

  mounted() {
    this.fetchBookings()
  },

  watch: {
    search()        { this.page = 1 },
    filterStatus()  { this.page = 1 },
    filterPayment() { this.page = 1 },
  },
}
</script>

<style scoped>
/* ── Layout ── */
.admin-bookings {
  padding: 24px 28px;
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: #f6f5fb;
  min-height: 100vh;
}

/* ── Page header ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 22px;
}
.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #1e1e2e;
  margin: 0;
}
.page-sub {
  font-size: 0.82rem;
  color: #888;
  margin: 2px 0 0;
}
.header-stats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.stat-chip {
  background: #fff;
  border: 1.5px solid #e0daf5;
  border-radius: 10px;
  padding: 8px 16px;
  text-align: center;
  min-width: 68px;
}
.stat-chip.booked    { border-color: #9e52eb; background: #f3edff; }
.stat-chip.cancelled { border-color: #ef4444; background: #fff5f5; }
.stat-chip.completed { border-color: #22c55e; background: #f0fdf4; }
.stat-num   { display: block; font-size: 1.3rem; font-weight: 800; color: #1e1e2e; }
.stat-label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Toolbar ── */
.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 18px;
}
.search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
}
.search-input {
  width: 100%;
  padding: 9px 36px 9px 32px;
  border: 1.5px solid #e0daf5;
  border-radius: 8px;
  font-size: 0.9rem;
  background: #fff;
  outline: none;
  transition: border-color .2s;
}
.search-input:focus { border-color: #9e52eb; }
.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 0.85rem;
}
.filter-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.filter-select {
  padding: 8px 12px;
  border: 1.5px solid #e0daf5;
  border-radius: 8px;
  font-size: 0.85rem;
  background: #fff;
  color: #333;
  outline: none;
  cursor: pointer;
}
.filter-select:focus { border-color: #9e52eb; }
.refresh-btn {
  padding: 8px 16px;
  background: #9e52eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
}
.refresh-btn:hover:not(:disabled) { background: #7c3fc2; }
.refresh-btn:disabled { opacity: .6; cursor: not-allowed; }

/* ── Skeleton ── */
.skeleton-wrap { display: flex; flex-direction: column; gap: 10px; }
.skeleton-row {
  height: 46px;
  background: linear-gradient(90deg, #ece9f7 25%, #f5f3fc 50%, #ece9f7 75%);
  background-size: 200% 100%;
  animation: shimmer 1.3s infinite;
  border-radius: 8px;
}
@keyframes shimmer { to { background-position: -200% 0; } }

/* ── Empty ── */
.empty-state {
  text-align: center;
  padding: 56px 0;
  color: #aaa;
}
.empty-icon { font-size: 2.6rem; margin-bottom: 10px; }
.empty-msg  { font-size: 1rem; margin-bottom: 12px; }

/* ── Table ── */
.table-wrap {
  background: #fff;
  border-radius: 12px;
  border: 1.5px solid #e8e4f6;
  overflow-x: auto;
}
.bookings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
.bookings-table thead tr {
  background: #f3edff;
  border-bottom: 2px solid #e0daf5;
}
.bookings-table th {
  padding: 12px 14px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7c3fc2;
  white-space: nowrap;
}
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #5b2ea0; }
.sort-arrow { opacity: .55; font-size: 0.7rem; }

.booking-row {
  border-bottom: 1px solid #f0edf9;
  cursor: pointer;
  transition: background .15s;
}
.booking-row:last-child { border-bottom: none; }
.booking-row:hover { background: #faf8ff; }

.bookings-table td { padding: 11px 14px; vertical-align: middle; }

.booking-id {
  font-weight: 700;
  color: #9e52eb;
  font-size: 0.82rem;
}
.user-pill {
  background: #ede9fb;
  color: #5b2ea0;
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 0.78rem;
  font-weight: 600;
}
.trek-name {
  font-weight: 600;
  color: #333;
}
.date-cell { color: #666; font-size: 0.83rem; }
.center-cell { text-align: center; }
.people-badge { font-size: 0.82rem; color: #555; }

/* ── Status / Payment badges ── */
.status-badge, .payment-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.03em;
}
.status-booked    { background: #ede9fb; color: #7c3fc2; }
.status-cancelled { background: #fee2e2; color: #b91c1c; }
.status-completed { background: #dcfce7; color: #15803d; }
.pay-paid    { background: #dcfce7; color: #15803d; }
.pay-pending { background: #fef9c3; color: #854d0e; }
.pay-failed  { background: #fee2e2; color: #b91c1c; }

/* ── Action buttons ── */
.action-btn {
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  margin-right: 4px;
  transition: opacity .15s;
}
.action-btn:hover { opacity: .8; }
.view-btn   { background: #ede9fb; color: #7c3fc2; }
.cancel-btn { background: #fee2e2; color: #b91c1c; }

/* ── Pagination ── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 18px;
}
.page-btn {
  padding: 6px 16px;
  border: 1.5px solid #e0daf5;
  border-radius: 8px;
  background: #fff;
  color: #7c3fc2;
  font-weight: 600;
  cursor: pointer;
  transition: border-color .2s;
}
.page-btn:hover:not(:disabled) { border-color: #9e52eb; }
.page-btn:disabled { opacity: .4; cursor: not-allowed; }
.page-info { font-size: 0.85rem; color: #666; }

/* ── Modal overlay ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(20, 10, 40, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}
.modal-card {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(100, 60, 200, 0.18);
}
.modal-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px 14px;
  border-bottom: 1.5px solid #f0edf9;
}
.modal-title-text {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e1e2e;
  margin: 0 0 6px;
}
.modal-close {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #aaa;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}
.modal-close:hover { color: #555; }

.modal-body-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 16px;
  padding: 20px 24px;
}
.detail-block { }
.detail-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #999;
  margin-bottom: 4px;
}
.detail-value {
  font-size: 0.92rem;
  font-weight: 600;
  color: #1e1e2e;
}
.id-tag {
  font-size: 0.72rem;
  color: #aaa;
  font-weight: 400;
  margin-left: 4px;
}

/* ── Participants in modal ── */
.participants-section {
  padding: 0 24px 20px;
}
.participants-heading {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #9e52eb;
  margin-bottom: 10px;
}
.no-participants {
  color: #bbb;
  font-size: 0.85rem;
  padding: 8px 0;
}
.participants-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.83rem;
}
.participants-table th {
  background: #f3edff;
  padding: 8px 10px;
  text-align: left;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #7c3fc2;
}
.participants-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #f5f2fb;
  color: #333;
}
.participants-table tr:last-child td { border-bottom: none; }
.aadhar-cell { font-family: monospace; color: #777; }

.modal-footer-bar {
  padding: 14px 24px 18px;
  border-top: 1.5px solid #f0edf9;
  text-align: right;
}
</style>