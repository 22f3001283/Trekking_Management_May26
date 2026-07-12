<template>
    <div>
        <!-- ── Navbar ── -->
        <nav class="navbar navbar-expand navbar-dark position-absolute top-0 start-0 end-0 z-3 px-4 py-3 custom-navbar">
            <router-link to="/" class="navbar-brand d-flex align-items-center gap-2 mb-0">
                <img :src="brandIcon" alt="" class="brand-icon" />
                <span class="fw-bold">Trek<span class="text-brand">Assist</span></span>
            </router-link>
            <div class="ms-auto d-flex gap-2">
                <router-link to="/login" class="btn btn-outline-light rounded-pill px-4">Login</router-link>
                <router-link to="/signup" class="btn btn-brand rounded-pill px-4">Signup</router-link>
            </div>
        </nav>

        <!-- ── Hero ── -->
        <section class="hero-section d-flex align-items-start" :style="{ backgroundImage: `url(${homeImg})` }">
            <div class="hero-overlay-gradient"></div>

            <div class="container position-relative z-2 py-5" style="margin-top: 80px;">
                <div class="row">
                    <div class="col-lg-6 d-flex flex-column gap-4">

                        <div>
                            <h1 class="display-5 fw-bold text-white lh-sm">Your Journey<br />Starts Here</h1>
                            <p class="text-white-50 mb-0">Plan. Trek. Enjoy. Repeat.</p>
                        </div>

                        <!-- KPIs -->
                        <div class="row row-cols-3 g-2" v-if="stats">
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.completion_rate_pct }}%</div>
                                    <div class="small text-uppercase text-muted">Treks Completed</div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.upcoming_treks }}</div>
                                    <div class="small text-uppercase text-muted">Open for Booking</div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.unique_participants }}</div>
                                    <div class="small text-uppercase text-muted">Trekkers Joined</div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.unique_treks_offered }}</div>
                                    <div class="small text-uppercase text-muted">Unique Treks Offered</div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.unique_destinations }}</div>
                                    <div class="small text-uppercase text-muted">Destinations</div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm text-center py-3">
                                    <div class="fs-4 fw-bold text-brand">{{ stats.total_participant_days }}</div>
                                    <div class="small text-uppercase text-muted">Trek-Days Delivered</div>
                                </div>
                            </div>
                        </div>

                        <!-- Secondary facts -->
                        <div class="card border-0 shadow-sm" v-if="stats">
                            <div class="card-body d-flex flex-wrap">
                                <div class="px-3 py-1 fact-item" v-if="difficultyMixText">
                                    <div class="small text-uppercase text-muted">Currently open</div>
                                    <div class="fw-semibold">{{ difficultyMixText }}</div>
                                </div>
                                <div class="px-3 py-1 fact-item" v-if="stats.busiest_month">
                                    <div class="small text-uppercase text-muted">Busiest season</div>
                                    <div class="fw-semibold">{{ stats.busiest_month }}</div>
                                </div>
                                <div class="px-3 py-1 fact-item">
                                    <div class="small text-uppercase text-muted">This year</div>
                                    <div class="fw-semibold">
                                        {{ stats.treks_this_year }} treks
                                        <span v-if="yoyChange !== null" :class="yoyChange >= 0 ? 'text-success' : 'text-danger'">
                                            ({{ yoyChange >= 0 ? '+' : '' }}{{ yoyChange }}%)
                                        </span>
                                    </div>
                                </div>
                                <div class="px-3 py-1 fact-item">
                                    <div class="small text-uppercase text-muted">Pace</div>
                                    <div class="fw-semibold">~{{ stats.avg_treks_per_month }}/month</div>
                                </div>
                                <div class="px-3 py-1 fact-item" v-if="stats.featured_trek">
                                    <div class="small text-uppercase text-muted">Most loved</div>
                                    <div class="fw-semibold">{{ stats.featured_trek }}</div>
                                </div>
                            </div>
                        </div>

                        <!-- Charts -->
                        <div class="row row-cols-1 row-cols-md-2 g-3" v-if="stats">
                            <div class="col">
                                <div class="card border-0 shadow-sm p-3">
                                    <h6 class="fw-bold text-muted mb-2">Participant Growth</h6>
                                    <div class="chart-canvas-wrap">
                                        <canvas ref="participantGrowthCanvas"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col">
                                <div class="card border-0 shadow-sm p-3">
                                    <h6 class="fw-bold text-muted mb-2">Treks Added Over Time</h6>
                                    <div class="chart-canvas-wrap">
                                        <canvas ref="trekGrowthCanvas"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </section>

        <footer class="bg-light text-center py-3 small">
            © 2026 Trekking Management. All rights reserved.
        </footer>
    </div>
</template>

<script>
import axios from 'axios'
import homeImg from "../assets/homePage.jpg"
import brandIcon from "../assets/icon.png"
import {
    Chart,
    LineController, LineElement, PointElement,
    CategoryScale, LinearScale,
    Tooltip
} from 'chart.js'

Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip)

export default {
    name: 'Home',
    data() {
        return {
            homeImg,
            brandIcon,
            stats: null,
            statsError: false,
            charts: {},
        }
    },
    computed: {
        difficultyMixText() {
            const mix = this.stats?.difficulty_mix
            if (!mix) return ''
            return Object.entries(mix)
                .map(([level, count]) => `${count} ${level}`)
                .join(' · ')
        },
        yoyChange() {
            const { treks_this_year, treks_last_year } = this.stats || {}
            if (!treks_last_year) return null
            return Math.round(((treks_this_year - treks_last_year) / treks_last_year) * 100)
        },
    },
    methods: {
        async fetchStats() {
            try {
                const res = await axios.get('http://127.0.0.1:5000/public/stats')

                // console.log("Entire response:", res)
                // console.log("Data:", res.data)

                this.stats = res.data
                this.$nextTick(() => this.renderCharts())
            } catch (e) {
                this.statsError = true
            }
        },
        destroyCharts() {
            Object.values(this.charts).forEach(c => c?.destroy())
            this.charts = {}
        },
        renderCharts() {
            this.destroyCharts()
            const growth = this.stats.growth

            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'nearest' },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        backgroundColor: '#1f2937',
                        padding: 8,
                        displayColors: false,
                    },
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 5,
                        backgroundColor: '#4169e1',
                        borderColor: '#fff',
                        borderWidth: 1.5,
                    },
                },
                scales: {
                    x: {
                        display: true,
                        grid: { display: false },
                        border: { display: false },
                        ticks: { color: '#6b7280', font: { size: 10 } },
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: { color: '#f0f0f0' },
                        border: { display: false },
                        ticks: { color: '#6b7280', font: { size: 10 }, precision: 0 },
                    },
                },
            }

            this.charts.participants = new Chart(this.$refs.participantGrowthCanvas, {
                type: 'line',
                data: {
                    labels: growth.participants.labels,
                    datasets: [{
                        data: growth.participants.data,
                        borderColor: '#4169e1',
                        backgroundColor: 'rgba(65,105,225,0.18)',
                        tension: 0.3,
                        fill: true,
                    }]
                },
                options: chartOptions
            })

            this.charts.treks = new Chart(this.$refs.trekGrowthCanvas, {
                type: 'line',
                data: {
                    labels: growth.treks.labels,
                    datasets: [{
                        data: growth.treks.data,
                        borderColor: '#4169e1',
                        backgroundColor: 'rgba(65,105,225,0.05)',
                        tension: 0.3,
                        fill: true,
                    }]
                },
                options: chartOptions
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
.custom-navbar {
    background: linear-gradient(180deg, rgba(17,24,39,0.6) 0%, rgba(17,24,39,0) 100%);
}
.brand-icon {
    height: 40px;
    width: 40px;
    object-fit: contain;
}
.text-brand {
    color: #4169e1;
}
.btn-brand {
    background: #4169e1;
    border-color: #4169e1;
    color: #fff;
}
.btn-brand:hover {
    background: #3557c2;
    border-color: #3557c2;
    color: #fff;
}
.hero-section {
    position: relative;
    min-height: 100vh;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
.hero-overlay-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.25) 45%, rgba(0,0,0,0) 70%);
    z-index: 1;
}
.fact-item {
    border-right: 1px solid #e5e7eb;
}
.fact-item:last-child {
    border-right: none;
}
.chart-canvas-wrap {
    position: relative;
    height: 140px;
    width: 100%;
}
</style>