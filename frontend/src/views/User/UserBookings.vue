<template>
    <UserNavbar />

    <div class="container-fluid  responsive-container" style="margin-top: 100px;">

        <!-- ══════════════════ BOOKED TREKS ══════════════════ -->
        <div class="d-flex justify-content-end mb-3">
            <button class="btn btn-sm btn-primary" @click="exportHistory">
                <i class="bi bi-download"></i>   Export Booking History
            </button>
        </div>
        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-3">
            <h2 class="mb-0">My Bookings</h2>
            <!-- Booked Treks Search/Sort/Filter -->
            <div class="d-flex flex-column flex-sm-row gap-2 mb-3 align-items-right justify-content-end">
                <div class="input-group" style="max-width: 370px;">
                    <input class="form-control" type="search" v-model="bookedSearchQuery"
                        :placeholder="'Search by ' + bookedSearchField.replace('_', ' ') + '...'" aria-label="Search">
                    <select class="form-select" v-model="bookedSearchField" style="max-width: 180px;">
                        <option value="trek_name">Trek Name</option>
                        <option value="booking_date">Date</option>
                        <option value="status">Booking Status</option>
                        <option value="payment_status">Payment Status</option>
                    </select>
                </div>

                <!-- Booked Sort -->
                <div class="dropdown">
                    <button class="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        <i class="bi bi-sort-alpha-down"></i> Sort
                    </button>
                    <div class="dropdown-menu p-3" style="min-width: 220px;">
                        <label class="form-label fw-bold">Sort By</label>
                        <select class="form-select" v-model="bookedSortBy">
                            <option value="">None</option>
                            <option value="date_desc">Booking Date: Newest First</option>
                            <option value="date_asc">Booking Date: Oldest First</option>
                            <option value="name_asc">Trek Name: A → Z</option>
                            <option value="name_desc">Trek Name: Z → A</option>
                        </select>
                    </div>
                </div>

                <!-- Booked Filter -->
                <div class="dropdown">
                    <button class="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        <i class="bi bi-funnel"></i> Filter
                    </button>
                    <div class="dropdown-menu p-3" style="min-width: 260px;">
                        <label class="form-label fw-bold">Booking Status</label>
                        <select class="form-select mb-3" v-model="bookedFilterStatus">
                            <option value="">All</option>
                            <option value="Booked">Booked</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                        <label class="form-label fw-bold">Payment Status</label>
                        <select class="form-select mb-3" v-model="bookedFilterPayment">
                            <option value="">All</option>
                            <option value="Paid">Paid</option>
                            <option value="Pending">Pending</option>
                            <option value="Refund">Refund</option>
                        </select>
                        <button class="btn btn-outline-danger w-100" @click="resetBookedFilters">Reset Filters</button>
                    </div>
                </div>
            </div>            
        </div>

        <div v-if="filteredBookings.length > 0" class="row g-3 mb-5">
            <div v-for="b in filteredBookings" :key="b.booking_id" class="col-md-4 col-lg-3">
                <div class="card h-100 booked-card">
                    <div class="card-body">
                        <h5 class="card-title">{{ getTrekName(b.trek_id) }}</h5>
                        <p class="card-text">
                            <strong>Booked On:</strong> {{ formatDate(b.booking_date) }}<br>
                            <strong>Trek Dates:</strong> {{ getTrekById(b.trek_id)?.start_date || '—' }} → {{ getTrekById(b.trek_id)?.end_date || '—' }}<br>
                            <strong>Status:</strong>
                            <span :class="bookingStatusClass(b.status)">{{ b.status }}</span><br>
                            <strong>Payment:</strong>
                            <span :class="paymentStatusClass(b.payment_status)">{{ b.payment_status }}</span>
                        </p>
                        <div class="d-flex gap-2 flex-wrap">
                            <button class="btn btn-sm btn-outline-primary"
                                @click="handleViewTrekClick(b)"
                                data-bs-toggle="modal"
                                data-bs-target="#trekModal">
                                View Trek
                            </button>
                            <button v-if="b.status !== 'Completed' && b.trek?.status === 'Open'"
                                class="btn btn-sm btn-outline-secondary"
                                @click="handleEditBookingClick(b)">
                                Edit Booking
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info mb-5">No bookings found.</div>
    </div>
    <!-- Booking Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ existingBooking ? 'Edit Booking' : 'Book Trek' }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-0" style="margin: 20px; margin-top: 0;">
                    <Booking
                        v-if="currentBookingTrek"
                        :key="currentBookingTrek.trek_id + '_' + (existingBooking ? existingBooking.booking_id : 'new')"
                        :mode="existingBooking ? 'edit' : 'create'"
                        :trek="currentBookingTrek"
                        :booking="existingBooking"
                        @submit="onBooked"
                        @cancel="closeBookingModal"
                        @deleted="onBookingDeleted"
                    />
                </div>
            </div>
        </div>
    </div>

    <!-- View Trek Modal -->
    <div class="modal fade" id="trekModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Trek Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <Trek
                        v-if="currentTrek"
                        :key="currentTrek.trek_id"
                        mode="view"
                        :trek="currentTrek"
                        @cancel="handleCancel"
                        @viewReviews="goToReviews"
                    />
                </div>
            </div>
        </div>
    </div>
    <footer class="bg-light text-center py-3 small" style="margin-top: 20px">
        © 2026 Trekking Management. All rights reserved.
    </footer>        
</template>

<script>
import axios from 'axios'
import TrekDefault from '../../assets/TrekDefault.png'
import Trek from '../../components/Trek.vue'
import Booking from '../../components/Booking.vue'
import UserNavbar from '../../components/UserNavbar.vue'

export default {
    components: { Trek, UserNavbar, Booking },
    data() {
        return {
            userId: parseInt(this.$route.params.user_id),
            TrekDefault,
            treks: [],
            userBookings: [],
            
            // Available treks search/sort/filter
            searchQuery: '',
            searchField: 'trek_name',
            sortBy: '',
            filterDifficulty: '',
            filterMinPrice: '',
            filterMaxPrice: '',

            // Booked treks search/sort/filter
            bookedSearchQuery: '',
            bookedSearchField: 'trek_name',
            bookedSortBy: 'date_desc',
            bookedFilterStatus: '',
            bookedFilterPayment: '',

            // Modal state
            currentTrek: null,
            currentBookingTrek: null,
            existingBooking: null,
        }
    },
    computed: {
        // ── Available treks ──
        filteredTreks() {
            let result = this.treks
            if (this.searchQuery) {
                result = result.filter(trek => {
                    const val = trek[this.searchField]
                    if (val === null || val === undefined) return false
                    return val.toString().toLowerCase().includes(this.searchQuery.toLowerCase())
                })
            }
            if (this.filterDifficulty)
                result = result.filter(t => t.difficulty === this.filterDifficulty)
            if (this.filterMinPrice !== '')
                result = result.filter(t => t.price >= parseFloat(this.filterMinPrice))
            if (this.filterMaxPrice !== '')
                result = result.filter(t => t.price <= parseFloat(this.filterMaxPrice))
            if (this.sortBy === 'price_asc')  result = [...result].sort((a, b) => a.price - b.price)
            else if (this.sortBy === 'price_desc') result = [...result].sort((a, b) => b.price - a.price)
            else if (this.sortBy === 'duration')   result = [...result].sort((a, b) => a.duration_days - b.duration_days)
            return result
        },

        // ── Booked treks ──
        filteredBookings() {
            let result = [...this.userBookings]

            if (this.bookedSearchQuery) {
                const q = this.bookedSearchQuery.toLowerCase()
                result = result.filter(b => {
                    if (this.bookedSearchField === 'trek_name')
                        return this.getTrekName(b.trek_id).toLowerCase().includes(q)
                    if (this.bookedSearchField === 'booking_date')
                        return this.formatDate(b.booking_date).toLowerCase().includes(q)
                    const val = b[this.bookedSearchField]
                    return val ? val.toString().toLowerCase().includes(q) : false
                })
            }

            if (this.bookedFilterStatus)
                result = result.filter(b => b.status === this.bookedFilterStatus)
            if (this.bookedFilterPayment)
                result = result.filter(b => b.payment_status === this.bookedFilterPayment)

            if (this.bookedSortBy === 'date_desc')
                result = [...result].sort((a, b) => new Date(b.booking_date) - new Date(a.booking_date))
            else if (this.bookedSortBy === 'date_asc')
                result = [...result].sort((a, b) => new Date(a.booking_date) - new Date(b.booking_date))
            else if (this.bookedSortBy === 'name_asc')
                result = [...result].sort((a, b) => this.getTrekName(a.trek_id).localeCompare(this.getTrekName(b.trek_id)))
            else if (this.bookedSortBy === 'name_desc')
                result = [...result].sort((a, b) => this.getTrekName(b.trek_id).localeCompare(this.getTrekName(a.trek_id)))

            return result
        },

    },
    methods: {
        async fetchTreks() {
            try {
                const token = localStorage.getItem('token')
                const res = await axios.get('http://127.0.0.1:5000/user/treks', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.treks = res.data
            } catch (e) { console.error('Error fetching treks:', e) }
        },

        async fetchUserBookings() {
            try {
                const token = localStorage.getItem('token')
                const res = await axios.get('http://127.0.0.1:5000/user/bookings', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.userBookings = res.data
            } catch (e) { this.userBookings = [] }
        },

        getTrekName(trekId) {
            const b = this.userBookings.find(b => b.trek_id === trekId)
            return b?.trek?.trek_name || `Trek #${trekId}`
        },

        getTrekById(trekId) {
            const b = this.userBookings.find(b => b.trek_id === trekId)
            return b?.trek || null
        },

        async exportHistory() {
            const token = localStorage.getItem('token')
            try {
                const res = await axios.post('http://127.0.0.1:5000/export/booking-history', {}, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.pollExportStatus(res.data.task_id)
            } catch (e) {
                alert(e.response?.data?.msg || 'Failed to start export.')
            }
        },

        pollExportStatus(taskId) {
            const token = localStorage.getItem('token')
            const interval = setInterval(async () => {
                try {
                    const res = await axios.get(`http://127.0.0.1:5000/export/status/${taskId}`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
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
            const token = localStorage.getItem('token')
            try {
                const res = await axios.get(`http://127.0.0.1:5000/export/download/${filename}`, {
                    headers: { Authorization: `Bearer ${token}` },
                    responseType: 'blob'
                })
                const url = window.URL.createObjectURL(new Blob([res.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', filename)
                document.body.appendChild(link)
                link.click()
                link.remove()
                alert('Booking history downloaded successfully!')
            } catch (e) {
                alert('Failed to download file.')
            }
        },

        handleViewClick(trek) { this.currentTrek = trek },

        async handleBookClick(trek) {
            this.currentBookingTrek = trek
            this.existingBooking = null
            await this.fetchUserBookings()
            const existing = this.userBookings.find(b => b.trek_id === trek.trek_id && b.status !== 'Cancelled')
            this.existingBooking = existing || null
            await this.$nextTick()
            let modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'))
            if (!modal) modal = new bootstrap.Modal(document.getElementById('bookingModal'))
            modal.show()
        },

        handleViewTrekClick(booking) {
            const trek = this.getTrekById(booking.trek_id)
            if (trek) this.currentTrek = trek
        },

        async handleEditBookingClick(booking) {
            const trek = this.getTrekById(booking.trek_id)
            if (!trek) return alert('Trek details not found.')
            this.currentBookingTrek = trek
            this.existingBooking = booking
            await this.$nextTick()
            let modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'))
            if (!modal) modal = new bootstrap.Modal(document.getElementById('bookingModal'))
            modal.show()
        },

        handleCancel() {
            bootstrap.Modal.getInstance(document.getElementById('trekModal'))?.hide()
        },

        onBooked(result) {
            this.closeBookingModal()
            this.fetchTreks()
            this.fetchUserBookings()
            alert(`Booking confirmed! ID: #${result.booking.booking_id}`)
        },

        onBookingDeleted() {
            this.closeBookingModal()
            this.currentBookingTrek = null 
            this.existingBooking = null   
            this.fetchTreks() 
            this.fetchUserBookings()
        },

        closeBookingModal() {
            const modalEl = document.getElementById('bookingModal')
            const modal = bootstrap.Modal.getInstance(modalEl)
            if (modal) {
                modalEl.addEventListener('hidden.bs.modal', () => {
                    this.currentBookingTrek = null
                    this.existingBooking = null
                }, { once: true })
                modal.hide()
            } else {
                this.currentBookingTrek = null
                this.existingBooking = null
            }
        },

        resetBookedFilters() {
            this.bookedSearchQuery   = ''
            this.bookedSearchField   = 'trek_name'
            this.bookedSortBy        = 'date_desc'
            this.bookedFilterStatus  = ''
            this.bookedFilterPayment = ''
        },

        resetFilters() {
            this.searchQuery      = ''
            this.searchField      = 'trek_name'
            this.sortBy           = ''
            this.filterDifficulty = ''
            this.filterMinPrice   = ''
            this.filterMaxPrice   = ''
        },

        formatDate(iso) {
            if (!iso) return '—'
            return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
        },

        bookingStatusClass(status) {
            return {
                'text-success fw-bold': status === 'Booked',
                'text-danger fw-bold':  status === 'Cancelled',
                'text-primary fw-bold': status === 'Completed',
            }
        },

        paymentStatusClass(status) {
            return {
                'text-success fw-bold': status === 'Paid',
                'text-warning fw-bold': status === 'Pending',
                'text-danger fw-bold':  status === 'Refund',
            }
        },
    },
    mounted() {
        this.fetchTreks()
        this.fetchUserBookings()
        document.getElementById('bookingModal').addEventListener('hidden.bs.modal', () => {
            this.currentBookingTrek = null
            this.existingBooking = null
        })
    }
}
</script>

<style scoped>
h2 {
    font-weight: 600;
    color: #1b2430;
    letter-spacing: -0.01em;
}

.btn {
    opacity: 1 !important;
    font-weight: 500;
}

.btn-primary {
    background-color: #4169e1;
    border-color: #4169e1;
}
.btn-primary:hover {
    background-color: #3457c4;
    border-color: #3457c4;
}

.btn-outline-primary {
    color: #4169e1;
    border-color: #4169e1;
}
.btn-outline-primary:hover {
    background-color: #4169e1;
    border-color: #4169e1;
    color: #fff;
}

.card {
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.card:hover {
    border-color: #c7d1f2;
    box-shadow: 0 4px 14px rgba(23, 43, 99, 0.08);
}

.booked-card {
    border: 1px solid #dfe3ea;
}

.card-title {
    font-weight: 600;
    color: #1b2430;
}

.card-text {
    color: #4b5563;
    font-size: 0.92rem;
}

.dropdown-menu {
    border: 1px solid #dfe3ea;
    box-shadow: 0 6px 18px rgba(23, 43, 99, 0.1);
}

.form-select:focus,
.form-control:focus {
    border-color: #4169e1;
    box-shadow: 0 0 0 0.2rem rgba(65, 105, 225, 0.15);
}

.alert-info {
    background-color: #eef1fc;
    border-color: #d9e0f7;
    color: #33415e;
}

.responsive-container {
    padding-left: 20px;
    padding-right: 20px;
}

@media (min-width: 992px) {
    .responsive-container {
        padding-left: 100px;
        padding-right: 100px;
    }
}
</style>