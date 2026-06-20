<template>
  <div class="admin-bookings">
    <UserNavbar />
    <!-- ── Page header ── -->
    <div class="page-header" style="margin-top: 40px;">
      <div>
        <button class="btn btn-outline-secondary btn-sm mb-2" @click="$router.back()">← Home</button>
        <h4 class="page-title">All Bookings</h4>
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
          placeholder="Search by booking ID, username, trek name…"
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
    <div v-if="loading" class="d-flex flex-column gap-3">
      <div v-for="n in 4" :key="n" class="skeleton-card"></div>
    </div>

    <!-- ── Empty state ── -->
    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-icon">🏔️</div>
      <p class="empty-msg">No bookings match your filters.</p>
      <button class="btn btn-sm btn-outline-secondary" @click="clearFilters">Clear filters</button>
    </div>

    <!-- ── Booking Cards ── -->
    <div v-else class="d-flex flex-column gap-3">
      <div
        v-for="b in paginated"
        :key="b.booking_id"
        class="booking-card"
      >
        <!-- Card top row -->
        <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
          <div>
            <div class="booking-trek-name">{{ getTrekName(b.trek_id) }}</div>
            <div class="booking-meta">
              🆔 Booking #{{ b.booking_id }} &nbsp;·&nbsp;
              👤 {{ getUserName(b.user_id) }} &nbsp;·&nbsp;
              📅 {{ formatDate(b.booking_date) }} &nbsp;·&nbsp;
              👥 {{ b.num_people }} participant(s) &nbsp;·&nbsp;
              📍 {{ getTrekLocation(b.trek_id) }}
            </div>
          </div>
          <div class="d-flex flex-column align-items-end gap-1">
            <span :class="statusBadge(b.status)">Booking: {{ b.status }}</span>
            <span :class="paymentBadge(b.payment_status)">Payment: {{ b.payment_status }}</span>
          </div>
        </div>

        <!-- Participants toggle + cancel -->
        <div class="mt-3 d-flex align-items-center gap-2 flex-wrap">
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="toggleParticipants(b.booking_id)"
          >
            {{ expanded === b.booking_id ? 'Hide' : 'View' }} Participants
          </button>
          <button
            v-if="b.status === 'Booked' && b.trek?.status === 'Open'"
            class="btn btn-sm btn-outline-danger"
            @click="cancelBooking(b)"
          >
            ✕ Cancel Booking
          </button>
        </div>

        <!-- Participants table (expanded) -->
        <div v-if="expanded === b.booking_id" class="mt-2">
          <div v-if="!participants[b.booking_id]" class="text-muted small">
            <span class="spinner-border spinner-border-sm me-1"></span> Loading…
          </div>
          <table v-else class="table table-sm table-bordered mb-0 mt-2">
            <thead class="participants-thead">
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>DOB</th>
                <th>Aadhar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in participants[b.booking_id]" :key="p.participant_id">
                <td>{{ i + 1 }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.dob }}</td>
                <td class="aadhar-cell">{{ maskAadhar(p.aadhar) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- ── Pagination ── -->
    <div v-if="totalPages > 1" class="pagination-bar">
      <button class="page-btn" :disabled="page === 1" @click="page--">‹ Prev</button>
      <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
      <button class="page-btn" :disabled="page === totalPages" @click="page++">Next ›</button>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
import UserNavbar from '../../components/UserNavbar.vue';
const BASE = 'http://127.0.0.1:5000'

export default {
  name: 'AdminBookings',
  components: { UserNavbar },
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

      page: 1,
      perPage: 10,

      expanded: null,       // booking_id currently expanded
      participants: {},     // { booking_id: [...] }
    }
  },

  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.bookings.filter(b => {
        const matchSearch =
          !q ||
          String(b.booking_id).includes(q) ||
          this.getUserName(b.user_id).toLowerCase().includes(q) ||
          this.getTrekName(b.trek_id).toLowerCase().includes(q)

        const matchStatus  = !this.filterStatus  || b.status === this.filterStatus
        const matchPayment = !this.filterPayment || b.payment_status === this.filterPayment

        return matchSearch && matchStatus && matchPayment
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
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },

    async fetchBookings() {
      this.loading = true
      this.error   = ''
      try {
        const [bRes, uRes, tRes] = await Promise.all([
          axios.get(`http://127.0.0.1:5000/bookings`, { headers: this.authHeader() }),
          axios.get(`http://127.0.0.1:5000/users`,    { headers: this.authHeader() }),
          axios.get(`http://127.0.0.1:5000/treks`,    { headers: this.authHeader() }),
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

    async toggleParticipants(bookingId) {
      if (this.expanded === bookingId) {
        this.expanded = null
        return
      }
      this.expanded = bookingId
      if (this.participants[bookingId]) return  // already loaded

      try {
        const res = await axios.get(`http://127.0.0.1:5000/bookings/${bookingId}`, {
          headers: this.authHeader()
        })
        this.participants = { ...this.participants, [bookingId]: res.data.participants }
      } catch (e) {
        console.error('Failed to fetch participants', e)
        this.participants = { ...this.participants, [bookingId]: [] }
      }
    },

    async cancelBooking(booking) {
      if (!confirm(`Cancel Booking #${booking.booking_id}? This will restore trek slots.`)) return
      try {
        await axios.delete(`http://127.0.0.1:5000/bookings/${booking.booking_id}`, {
          headers: this.authHeader()
        })
        await this.fetchBookings()
        // reset expanded participants cache for this booking
        const updated = { ...this.participants }
        delete updated[booking.booking_id]
        this.participants = updated
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

    getTrekLocation(trekId) {
      const t = this.treks.find(t => t.trek_id === trekId)
      return t ? t.location : '—'
    },

    countByStatus(status) {
      return this.bookings.filter(b => b.status === status).length
    },

    formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: true,
      })
    },

    maskAadhar(aadhar) {
      if (!aadhar || aadhar.length < 4) return aadhar
      return 'XXXX XXXX ' + aadhar.slice(-4)
    },

    statusBadge(status) {
      return {
        badge: true,
        'bg-success':   status === 'Booked',
        'bg-danger':    status === 'Cancelled',
        'bg-secondary': status === 'Completed',
      }
    },

    paymentBadge(status) {
      return {
        badge: true,
        'bg-warning text-dark': status === 'Pending',
        'bg-success':           status === 'Paid',
        'bg-danger':            status === 'Failed',
      }
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
.admin-bookings {
  padding: 90px 100px 40px;
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
  margin-bottom: 20px;
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
.skeleton-card {
  height: 90px;
  background: linear-gradient(90deg, #ece9f7 25%, #f5f3fc 50%, #ece9f7 75%);
  background-size: 200% 100%;
  animation: shimmer 1.3s infinite;
  border-radius: 10px;
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

/* ── Booking card — matches History.vue style ── */
.booking-card {
  border: 1px solid #e4d9f9;
  border-radius: 10px;
  padding: 14px 16px;
  background: #fff;
}

.booking-trek-name {
  font-weight: 700;
  font-size: 1rem;
  color: #2d2d2d;
}

.booking-meta {
  font-size: 0.82rem;
  color: #666;
  margin-top: 4px;
}

/* ── Participants table header ── */
.participants-thead th {
  background: #f3edff;
  color: #7c3fc2;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.aadhar-cell { font-family: monospace; color: #777; }

/* ── Pagination ── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
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
</style>