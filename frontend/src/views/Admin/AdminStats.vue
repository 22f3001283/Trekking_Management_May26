<template>
    <AdminNavbar />

    <div class="container-fluid responsive-container" style="margin-top: 100px;">

        <div class="mb-4 d-flex justify-content-between align-items-center">
            <div>
                <h2 class="fw-bold mb-1">Platform Analytics</h2>
                <p class="text-muted small mb-0" style="margin-top: 3px;">Stats and trends across treks, bookings and users</p>
            </div>
            <button class="btn btn-sm btn-primary" @click="fetchStats" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>Refresh</span>
            </button>
        </div>

        <div v-if="error" class="alert alert-danger mb-4">{{ error }}</div>

        <!-- KPI Cards -->
        <div v-if="stats" class="row g-3 mb-5">
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Total Treks</div>
                        <div class="fs-3 fw-bold text-primary">{{ stats.kpis.total_treks }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Total Bookings</div>
                        <div class="fs-3 fw-bold text-primary">{{ stats.kpis.total_bookings }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Participants</div>
                        <div class="fs-3 fw-bold text-primary">{{ stats.kpis.total_participants }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Registered Users</div>
                        <div class="fs-3 fw-bold text-primary">{{ stats.kpis.total_users }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Confirmed Revenue</div>
                        <div class="fs-3 fw-bold text-primary">₹{{ stats.kpis.total_confirmed_revenue }}</div>
                    </div>
                </div>
            </div>
            <div class="col-6 col-md-2">
                <div class="card border h-100">
                    <div class="card-body p-4">
                        <div class="text-muted text-uppercase small mb-2" style="font-size: 0.65rem; letter-spacing: .07em;">Cancellation Rate</div>
                        <div class="fs-3 fw-bold text-primary">{{ stats.kpis.cancellation_rate }}%</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div v-if="stats" class="row g-4">
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Most Popular Treks</h6>
                    <canvas ref="popularTreksCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Booking Trends</h6>
                    <canvas ref="bookingTrendsCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Monthly Participation</h6>
                    <canvas ref="monthlyParticipationCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">User Registrations</h6>
                    <canvas ref="userRegistrationsCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Treks by Status (creation month)</h6>
                    <canvas ref="treksByStatusCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Revenue Trend</h6>
                    <canvas ref="revenueTrendCanvas" height="260"></canvas>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Booking Status</h6>
                    <canvas ref="bookingStatusCanvas" height="240"></canvas>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Difficulty Distribution</h6>
                    <canvas ref="difficultyCanvas" height="240"></canvas>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border p-4">
                    <h6 class="fw-bold mb-3">Cancellation Rate over Time</h6>
                    <canvas ref="cancellationRateCanvas" height="240"></canvas>
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
import AdminNavbar from '../../components/AdminNavbar.vue'
import {
    Chart,
    BarController, BarElement,
    LineController, LineElement, PointElement,
    DoughnutController, ArcElement,
    CategoryScale, LinearScale,
    Tooltip, Legend
} from 'chart.js'

Chart.register(
    BarController, BarElement,
    LineController, LineElement, PointElement,
    DoughnutController, ArcElement,
    CategoryScale, LinearScale,
    Tooltip, Legend
)

// Distinct multi-hue palette for charts — not tied to the blue brand color
const PALETTE = ['#4169e1', '#e07a3f', '#2fa86a', '#c0392b', '#8e5ac4', '#d4a017', '#1aa3a3', '#c2599a']

export default {
    name: 'AdminStats',
    components: { AdminNavbar },
    data() {
        return {
            stats: null,
            loading: false,
            error: '',
            charts: {}, // holds Chart.js instances so we can destroy on refresh
        }
    },
    methods: {
        authHeader() {
            return { Authorization: `Bearer ${localStorage.getItem('token')}` }
        },
        async fetchStats() {
            this.loading = true
            this.error = ''
            try {
                const res = await axios.get('http://127.0.0.1:5000/admin/stats', { headers: this.authHeader() })
                this.stats = res.data
                this.$nextTick(() => this.renderCharts())
            } catch (e) {
                this.error = e.response?.data?.msg || 'Failed to load stats.'
            } finally {
                this.loading = false
            }
        },
        destroyCharts() {
            Object.values(this.charts).forEach(c => c?.destroy())
            this.charts = {}
        },
        renderCharts() {
            this.destroyCharts()
            const c = this.stats.charts

            this.charts.popularTreks = new Chart(this.$refs.popularTreksCanvas, {
                type: 'bar',
                data: {
                    labels: c.popular_treks.labels,
                    datasets: [{ label: 'Participants', data: c.popular_treks.data, backgroundColor: PALETTE }]
                },
                options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
            })

            this.charts.bookingTrends = new Chart(this.$refs.bookingTrendsCanvas, {
                type: 'line',
                data: {
                    labels: c.booking_trends.labels,
                    datasets: [{ label: 'Bookings', data: c.booking_trends.data, borderColor: PALETTE[0], tension: 0.3 }]
                },
                options: { responsive: true }
            })

            this.charts.monthlyParticipation = new Chart(this.$refs.monthlyParticipationCanvas, {
                type: 'bar',
                data: {
                    labels: c.monthly_participation.labels,
                    datasets: [{ label: 'Participants', data: c.monthly_participation.data, backgroundColor: PALETTE[1] }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            })

            this.charts.userRegistrations = new Chart(this.$refs.userRegistrationsCanvas, {
                type: 'line',
                data: {
                    labels: c.user_registrations.labels,
                    datasets: [{ label: 'New Users', data: c.user_registrations.data, borderColor: PALETTE[2], tension: 0.3 }]
                },
                options: { responsive: true }
            })

            this.charts.treksByStatus = new Chart(this.$refs.treksByStatusCanvas, {
                type: 'bar',
                data: {
                    labels: c.treks_by_status.labels,
                    datasets: c.treks_by_status.datasets.map((d, i) => ({
                        ...d,
                        backgroundColor: PALETTE[i % PALETTE.length]
                    }))
                },
                options: {
                    responsive: true,
                    scales: { x: { stacked: true }, y: { stacked: true } }
                }
            })

            this.charts.revenueTrend = new Chart(this.$refs.revenueTrendCanvas, {
                type: 'line',
                data: {
                    labels: c.revenue_trend.labels,
                    datasets: [{ label: 'Revenue (₹)', data: c.revenue_trend.data, borderColor: PALETTE[3], tension: 0.3, fill: false }]
                },
                options: { responsive: true }
            })

            this.charts.bookingStatus = new Chart(this.$refs.bookingStatusCanvas, {
                type: 'doughnut',
                data: {
                    labels: c.booking_status_breakdown.labels,
                    datasets: [{ data: c.booking_status_breakdown.data, backgroundColor: PALETTE }]
                },
                options: { responsive: true }
            })

            this.charts.difficulty = new Chart(this.$refs.difficultyCanvas, {
                type: 'doughnut',
                data: {
                    labels: c.difficulty_distribution.labels,
                    datasets: [{ data: c.difficulty_distribution.data, backgroundColor: PALETTE }]
                },
                options: { responsive: true }
            })

            this.charts.cancellationRate = new Chart(this.$refs.cancellationRateCanvas, {
                type: 'bar',
                data: {
                    labels: c.cancellation_rate_trend.labels,
                    datasets: [{ label: 'Cancellation %', data: c.cancellation_rate_trend.data, backgroundColor: PALETTE[4] }]
                },
                options: { responsive: true, plugins: { legend: { display: false } } }
            })
        },
    },
    mounted() {
        this.fetchStats()
    },
    beforeUnmount() {
        this.destroyCharts()
    },
}
</script>

<style scoped>
.card {
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    transition: background-color 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.card:hover {
    border-color: #c7d1f2;
    background-color: #eef4ff;
    box-shadow: 0 4px 14px rgba(23, 43, 99, 0.08);
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