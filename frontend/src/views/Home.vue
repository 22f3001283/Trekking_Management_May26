<template>
	<div class="page">
		<header class="nav">
			<div>
                <h3>Trekking Management</h3>
            </div>
			<div class="nav-actions">
				<router-link to="/login" class="btn">Login</router-link>
				<router-link to="/signup" class="btn primary">Signup</router-link>
			</div>
		</header>

		<main class="hero-wrap">
			<img :src="homeImg" alt="Home" class="hero-img" />
		</main>

		<!-- Public Stats -->
		<section class="stats-section" v-if="stats">
			<h2 class="stats-title">Trekking, by the numbers</h2>

			<div class="stats-grid">
				<div class="stat-card">
					<div class="stat-value">{{ stats.completion_rate_pct }}%</div>
					<div class="stat-label">Treks Completed</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">{{ stats.upcoming_treks }}</div>
					<div class="stat-label">Open for Booking</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">{{ stats.unique_participants }}</div>
					<div class="stat-label">Trekkers Joined</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">{{ stats.unique_treks_offered }}</div>
					<div class="stat-label">Unique Treks Offered</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">{{ stats.unique_destinations }}</div>
					<div class="stat-label">Destinations</div>
				</div>
				<div class="stat-card">
					<div class="stat-value">{{ stats.total_participant_days }}</div>
					<div class="stat-label">Trek-Days Delivered</div>
				</div>
			</div>

			<div class="stats-secondary">
				<div class="mini-fact" v-if="difficultyMixText">
					<strong>Currently open:</strong> {{ difficultyMixText }}
				</div>
				<div class="mini-fact" v-if="stats.busiest_month">
					<strong>Busiest season:</strong> {{ stats.busiest_month }}
				</div>
				<div class="mini-fact">
					<strong>This year vs last:</strong>
					{{ stats.treks_this_year }} treks conducted
					<span v-if="yoyChange !== null" :class="yoyChange >= 0 ? 'up' : 'down'">
						({{ yoyChange >= 0 ? '+' : '' }}{{ yoyChange }}% vs last year)
					</span>
				</div>
				<div class="mini-fact">
					<strong>Pace:</strong> ~{{ stats.avg_treks_per_month }} treks/month
				</div>
				<div class="mini-fact" v-if="stats.featured_trek">
					<strong>Most loved trek:</strong> {{ stats.featured_trek }}
				</div>
			</div>

			<div class="charts-grid">
				<div class="chart-card">
					<h6>Participant Growth</h6>
					<canvas ref="participantGrowthCanvas" height="140"></canvas>
				</div>
				<div class="chart-card">
					<h6>Treks Added Over Time</h6>
					<canvas ref="trekGrowthCanvas" height="140"></canvas>
				</div>
			</div>
		</section>

		<section v-else-if="statsError" class="stats-section">
			<!-- fail silently/quietly on homepage, no scary error banner for visitors -->
		</section>

		<footer class="footer">© 2026 Trekking Management. All rights reserved.</footer>
	</div>
</template>

<script>
import axios from 'axios'
import homeImg from "../assets/homePage.jpg"
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

            this.charts.participants = new Chart(this.$refs.participantGrowthCanvas, {
                type: 'line',
                data: {
                    labels: growth.participants.labels,
                    datasets: [{
                        data: growth.participants.data,
                        borderColor: '#9e52eb',
                        backgroundColor: 'rgba(158,82,235,0.1)',
                        tension: 0.3,
                        fill: true,
                        pointRadius: 0,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
            })

            this.charts.treks = new Chart(this.$refs.trekGrowthCanvas, {
                type: 'line',
                data: {
                    labels: growth.treks.labels,
                    datasets: [{
                        data: growth.treks.data,
                        borderColor: '#20c997',
                        backgroundColor: 'rgba(32,201,151,0.1)',
                        tension: 0.3,
                        fill: true,
                        pointRadius: 0,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
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
.stats-section {
    padding: 48px 80px;
    background-color: #f6f5fb;
}
.stats-title {
    text-align: center;
    font-weight: 700;
    margin-bottom: 28px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.stat-card {
    background: #fff;
    border-radius: 10px;
    padding: 20px 12px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #9e52eb;
}
.stat-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: .05em;
    margin-top: 4px;
}
.stats-secondary {
    display: flex;
    flex-wrap: wrap;
    gap: 12px 32px;
    justify-content: center;
    margin-bottom: 32px;
    font-size: 0.9rem;
    color: #374151;
}
.mini-fact strong {
    color: #111827;
}
.up { color: #059669; }
.down { color: #dc2626; }
.charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
.chart-card {
    background: #fff;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.chart-card h6 {
    font-weight: 700;
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: #374151;
}
</style>