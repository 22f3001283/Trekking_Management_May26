<template>
    <UserNavbar />

    <div class="container-fluid" style="padding-left: 100px; padding-right: 100px; margin-top: 70px;">

        <!-- ══════════════════ BOOKED TREKS ══════════════════ -->
        <h2 class="mb-3">My Booked Treks</h2>

        <!-- Booked Treks Search/Sort/Filter -->
        <div class="d-flex gap-2 mb-3 align-items-right justify-content-end">
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
                <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                    data-bs-toggle="dropdown" data-bs-auto-close="outside">Sort</button>
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
                <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                    data-bs-toggle="dropdown" data-bs-auto-close="outside">Filter</button>
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
                            <button class="btn btn-sm text-white"
                                style="background-color: #9e52eb;"
                                @click="handleViewTrekClick(b)"
                                data-bs-toggle="modal"
                                data-bs-target="#trekModal">
                                View Trek
                            </button>
                            <button v-if="b.status !== 'Completed' && b.trek?.status === 'Open'"
                                class="btn btn-sm text-white"
                                style="background-color: #f0932b;"
                                @click="handleEditBookingClick(b)">
                                Edit Booking
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info mb-5">No bookings found.</div>

        <!-- ══════════════════ AVAILABLE TREKS ══════════════════ -->
        <div class="d-flex gap-2 mb-3 align-items-right justify-content-end">
            <div class="input-group" style="max-width: 370px;">
                <input class="form-control" type="search" v-model="searchQuery"
                    :placeholder="'Search by ' + searchField.replace('_', ' ') + '...'" aria-label="Search">
                <select class="form-select" v-model="searchField" style="max-width: 150px;">
                    <option value="trek_name">Trek Name</option>
                    <option value="location">Location</option>
                    <option value="difficulty">Difficulty</option>
                    <option value="price">Price</option>
                    <option value="available_slots">Available Slots</option>
                    <option value="assigned_staff_name">Guide</option>
                </select>
            </div>

            <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                    data-bs-toggle="dropdown" data-bs-auto-close="outside">Sort</button>
                <div class="dropdown-menu p-3" style="min-width: 220px;">
                    <label class="form-label fw-bold">Sort By</label>
                    <select class="form-select" v-model="sortBy">
                        <option value="">None</option>
                        <option value="price_asc">Price: Low to High</option>
                        <option value="price_desc">Price: High to Low</option>
                        <option value="duration">Duration</option>
                    </select>
                </div>
            </div>

            <div class="dropdown">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                    data-bs-toggle="dropdown" data-bs-auto-close="outside">Filter</button>
                <div class="dropdown-menu p-3" style="min-width: 280px;">
                    <label class="form-label fw-bold">Difficulty</label>
                    <select class="form-select mb-3" v-model="filterDifficulty">
                        <option value="">All</option>
                        <option value="Easy">Easy</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Hard">Hard</option>
                    </select>
                    <label class="form-label fw-bold">Price Range</label>
                    <div class="d-flex gap-2 mb-3">
                        <input class="form-control" type="number" v-model="filterMinPrice" placeholder="Min">
                        <input class="form-control" type="number" v-model="filterMaxPrice" placeholder="Max">
                    </div>
                    <button class="btn btn-outline-danger w-100" @click="resetFilters">Reset Filters</button>
                </div>
            </div>
        </div>

        <h2>Available Treks</h2>
        <div v-if="filteredTreks.length > 0" class="row g-4">
            <div v-for="trek in filteredTreks" :key="trek.trek_id" class="col-md-4 col-lg-3">
                <div class="card h-100">
                    <div v-if="trek.images && trek.images.filter(img => img.startsWith('data:')).length > 0">
                        <div :id="'carousel-' + trek.trek_id" class="carousel slide" data-bs-ride="carousel">
                            <div class="carousel-inner">
                                <div v-for="(img, index) in trek.images.filter(img => img.startsWith('data:'))"
                                    :key="index" :class="['carousel-item', index === 0 ? 'active' : '']">
                                    <img :src="img" class="d-block w-100" style="height: 180px; object-fit: cover;">
                                </div>
                            </div>
                            <template v-if="trek.images.filter(img => img.startsWith('data:')).length > 1">
                                <button class="carousel-control-prev" type="button"
                                    :data-bs-target="'#carousel-' + trek.trek_id" data-bs-slide="prev">
                                    <span class="carousel-control-prev-icon"></span>
                                </button>
                                <button class="carousel-control-next" type="button"
                                    :data-bs-target="'#carousel-' + trek.trek_id" data-bs-slide="next">
                                    <span class="carousel-control-next-icon"></span>
                                </button>
                            </template>
                        </div>
                    </div>
                    <img v-else :src="TrekDefault" class="card-img-top" style="height: 180px; object-fit: cover;">

                    <div class="card-body">
                        <h5 class="card-title">{{ trek.trek_name }}</h5>
                        <p class="card-text">
                            <strong>Location:</strong> {{ trek.location }}<br>
                            <strong>Difficulty:</strong> {{ trek.difficulty }}<br>
                            <strong>Duration:</strong> {{ trek.duration_days }} days<br>
                            <strong>Guide:</strong> {{ trek.assigned_staff_name || 'Not assigned' }}<br>
                            <strong>Available Slots:</strong> {{ trek.available_slots }}<br>
                            <strong>Price:</strong> ₹{{ trek.price }}/person<br>
                        </p>
                        <div class="d-flex gap-2 align-items-center">
                            <button class="btn btn-sm text-white"
                                style="background-color: #9e52eb;"
                                @click="handleViewClick(trek)"
                                data-bs-toggle="modal"
                                data-bs-target="#trekModal">
                                View
                            </button>
                            <button 
                                v-if="trek.status === 'Open'"
                                class="btn btn-sm text-white"
                                style="background-color: #28a745;"
                                @click="handleBookClick(trek)">
                                Book
                            </button>
                            <span v-else-if="trek.status === 'Approved'" class="text-muted small">
                                Available for booking soon...
                            </span>                            
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="alert alert-info mt-3">No treks available at the moment.</div>
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
            userId: parseInt(this.$route.params.id),
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
.booked-card {
    border: 1px solid #e4d9f9;
    border-left: 4px solid #9e52eb;
}
</style>