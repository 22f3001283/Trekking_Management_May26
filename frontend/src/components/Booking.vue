<template>
    <div class="container mt-4">
        <form @submit.prevent="handleSubmit" class="row g-3">

            <div class="col-12">
                <h3 v-if="mode === 'create'">Book Trek</h3>
                <h3 v-else-if="mode === 'edit'">Edit Booking</h3>
                <h3 v-else>View Booking</h3>
            </div>

            <!-- ── Trek Info (read-only banner) ── -->
            <div class="col-12" v-if="trek">
                <div class="trek-banner">
                    <div>
                        <div class="trek-banner-name">{{ trek.trek_name }}</div>
                        <div class="trek-banner-meta">
                            📍 {{ trek.location }} &nbsp;·&nbsp;
                            🏔️ {{ trek.difficulty }} &nbsp;·&nbsp;
                            📅 {{ trek.start_date }} → {{ trek.end_date }}
                        </div>
                    </div>
                    <div class="trek-banner-price">₹{{ trek.price }}<span>/person</span></div>
                </div>
            </div>

            <!-- ── View mode: booking meta ── -->
            <template v-if="isView && booking">
                <div class="col-md-4">
                    <label class="form-label">Booking ID</label>
                    <input type="text" class="form-control" :value="'#' + booking.booking_id" disabled>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Booking Date</label>
                    <input type="text" class="form-control" :value="formatDate(booking.booking_date)" disabled>
                </div>
                <div class="col-md-4">
                    <label class="form-label">No. of Participants</label>
                    <input type="text" class="form-control" :value="booking.num_people" disabled>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Booking Status</label>
                    <input type="text" class="form-control" :value="booking.status" disabled>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Payment Status</label>
                    <input type="text" class="form-control" :value="booking.payment_status" disabled>
                </div>
            </template>

            <!-- ── Participants section heading ── -->
            <div class="col-12 d-flex justify-content-between align-items-center mt-2">
                <label class="form-label fw-bold mb-0">Participants</label>
                <button
                    v-if="!isView"
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    @click="addParticipant"
                    :disabled="form.participants.length >= ((trek?.available_slots || 0) + (isEdit ? booking?.num_people || 0 : 0))"
                >
                    + Add Participant
                </button>
            </div>

            <!-- ── Empty state ── -->
            <div class="col-12" v-if="form.participants.length === 0">
                <div class="empty-participants">
                    <span v-if="!isView">Click <strong>+ Add Participant</strong> to begin.</span>
                    <span v-else>No participants on record.</span>
                </div>
            </div>

            <!-- ── Participant rows ── -->
            <div
                v-for="(p, i) in form.participants"
                :key="i"
                class="col-12 participant-card"
            >
                <div class="participant-card-header">
                    <span>Person {{ i + 1 }}</span>
                    <button
                        v-if="!isView"
                        type="button"
                        class="btn-remove"
                        @click="removeParticipant(i)"
                    >✕ Remove</button>
                </div>
                <div class="row g-2 mt-1">
                    <div class="col-md-4">
                        <label class="form-label">Full Name <span v-if="!isView" class="text-danger">*</span></label>
                        <input
                            v-model="p.name"
                            :disabled="isView"
                            type="text"
                            class="form-control"
                            placeholder="As per Aadhar"
                        >
                        <div v-if="errors[i]?.name" class="field-error">{{ errors[i].name }}</div>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Date of Birth <span v-if="!isView" class="text-danger">*</span></label>
                        <input
                            v-model="p.dob"
                            :disabled="isView"
                            type="date"
                            class="form-control"
                            :max="todayString"
                        >
                        <div v-if="errors[i]?.dob" class="field-error">{{ errors[i].dob }}</div>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Aadhar Number <span v-if="!isView" class="text-danger">*</span></label>
                        <input
                            v-model="p.aadhar"
                            :disabled="isView"
                            type="text"
                            class="form-control"
                            placeholder="12-digit number"
                            maxlength="12"
                            @input="p.aadhar = p.aadhar.replace(/\D/g, '')"
                        >
                        <div v-if="errors[i]?.aadhar" class="field-error">{{ errors[i].aadhar }}</div>
                    </div>
                </div>
            </div>

            <!-- ── Cost summary ── -->
            <div class="col-12" v-if="!isView && form.participants.length > 0">
                <div class="cost-summary">
                    <span>{{ form.participants.length }} × ₹{{ trek?.price || 0 }}</span>
                    <span class="cost-total">Total: ₹{{ totalCost }}</span>
                </div>
            </div>

            <!-- ── Error banner ── -->
            <div class="col-12" v-if="submitError">
                <div class="alert alert-danger py-2 mb-0">{{ submitError }}</div>
            </div>

            <!-- ── Action buttons ── -->
            <div class="col-12 text-center mt-3">
                <template v-if="!isView">
                    <button
                        type="submit"
                        class="btn btn-primary me-2"
                        style="background-color: #9e52eb;"
                        :disabled="isSubmitting || form.participants.length === 0"
                    >
                        <span v-if="isSubmitting && lastAction === 'save'"
                            class="spinner-border spinner-border-sm me-1"></span>
                        Save
                    </button>
                    <button
                        type="button"
                        class="btn btn-success me-2"
                        @click="handleBookAndPay"
                        :disabled="isSubmitting || form.participants.length === 0"
                        style="background-color: #28a745;"
                    >
                        <span v-if="isSubmitting && lastAction === 'pay'"
                            class="spinner-border spinner-border-sm me-1"></span>
                        Book &amp; Pay
                    </button>

                    <!-- NEW: Delete only in edit mode -->
                    <button
                        v-if="isEdit && booking"
                        type="button"
                        class="btn btn-danger me-2"
                        @click="handleDelete"
                        :disabled="isSubmitting"
                        style="background-color: #dc3545;"
                    >
                        Delete Booking
                    </button>

                </template>

                <button type="button" class="btn btn-secondary" @click="handleCancel"
                    style="background-color: #818285;">
                    {{ isView ? 'Close' : 'Cancel' }}
                </button>
            </div>

        </form>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Booking',
    props: {
        mode:    { type: String, default: 'create' },   // 'create' | 'view' | 'edit'
        trek:    { type: Object, default: null },        // always pass trek
        booking: { type: Object, default: null },        // for view mode: booking record
        bookingParticipants: { type: Array, default: () => [] }, // for view mode: participants list
    },
    emits: ['submit', 'cancel', 'deleted'],

    data() {
        return {
            form: {
                participants: [],   // [{ name, dob, aadhar }]
                payment_status: 'Pending',
            },
            errors: [],
            submitError: '',
            isSubmitting: false,
            lastAction: '',
        }
    },

    computed: {
        isView() { return this.mode === 'view' },
        isEdit() { return this.mode === 'edit' },

        todayString() {
            const today = new Date()
            const offset = today.getTimezoneOffset()
            const local  = new Date(today.getTime() - offset * 60000)
            return local.toISOString().slice(0, 10)
        },

        totalCost() {
            const price = this.trek?.price || 0
            return (price * this.form.participants.length).toLocaleString('en-IN')
        },
    },


    watch: {
    // When an existing booking is passed in edit mode, fetch its participants
        booking: {
            immediate: true,
            async handler(b) {
                if (!b) return
                if (this.mode === 'edit') {
                    // Fetch participants for this booking
                    try {
                    const token = localStorage.getItem('token')
                    const res = await axios.get(`http://127.0.0.1:5000/bookings/${b.booking_id}`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                    this.form.participants = res.data.participants.map(p => ({
                        name: p.name, dob: p.dob, aadhar: p.aadhar
                    }))
                    this.errors = this.form.participants.map(() => ({}))
                    } catch (e) {
                    console.error('Could not load existing participants', e)
                    }
                }
            }
        },
        bookingParticipants: {
            immediate: true,
            handler(list) {
                if (!list || !list.length) return
                // In view mode, show participants as read-only rows
                this.form.participants = list.map(p => ({
                    name:   p.name  || '',
                    dob:    p.dob   || '',
                    aadhar: p.aadhar|| '',
                }))
            }
        },
    },

    methods: {
        addParticipant() {
            this.form.participants.push({ name: '', dob: '', aadhar: '' })
            this.errors.push({})
        },

        removeParticipant(i) {
            this.form.participants.splice(i, 1)
            this.errors.splice(i, 1)
        },

        validate() {
            let valid = true
            this.errors = this.form.participants.map(p => {
                const e = {}
                if (!p.name.trim())               { e.name   = 'Name is required.';                    valid = false }
                if (!p.dob)                       { e.dob    = 'Date of birth is required.';            valid = false }
                if (!/^\d{12}$/.test(p.aadhar))   { e.aadhar = 'Aadhar must be exactly 12 digits.';    valid = false }
                return e
            })
            return valid
        },

        // Called by form @submit.prevent → Save
        handleSubmit() {
            this.submitWithPayment('Pending')
        },

        // Called by Book & Pay button
        handleBookAndPay() {
            this.submitWithPayment('Paid')
        },

        async submitWithPayment(paymentStatus) {
            this.submitError = ''
            if (this.isSubmitting) return
            if (this.form.participants.length === 0) {
                this.submitError = 'Add at least one participant before booking.'
                return
            }
            if (!this.validate()) return

            // ── Warn if editing a PAID booking ──
            if (this.isEdit && this.booking && this.booking.status !== 'Cancelled') {
                if (this.booking.payment_status === 'Paid') {
                    const proceed = confirm(
                        'Your current payment will be refunded, and this edit will create a new booking that requires payment again. Do you want to continue?'
                    )
                    if (!proceed) return
                } else if (this.booking.payment_status === 'Pending') {
                    const proceed = confirm(
                        'Editing this booking will cancel your current pending booking and create a new one. Do you want to continue?'
                    )
                    if (!proceed) return
                }
            }

            this.isSubmitting = true
            this.lastAction   = paymentStatus === 'Paid' ? 'pay' : 'save'
            const token = localStorage.getItem('token')
            const userId = localStorage.getItem('user_id') || this.$route?.params?.user_id

            try {
                // ── EDIT: cancel old booking first, then rebook ──
                if (this.isEdit && this.booking && this.booking.status !== 'Cancelled') {
                    await axios.delete(`http://127.0.0.1:5000/bookings/${this.booking.booking_id}`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                }

            // ─ Create new booking with current form data ──
            const payload = {
                trek_id:        this.trek.trek_id,
                user_id:        parseInt(userId),
                payment_status: paymentStatus,
                participants:   this.form.participants.map(p => ({
                    name:   p.name.trim(),
                    dob:    p.dob,
                    aadhar: p.aadhar,
                })),
            }

            
            const response = await axios.post('http://127.0.0.1:5000/bookings', payload, {
                headers: { Authorization: `Bearer ${token}` },
            })
            this.$emit('submit', response.data)

            } catch (err) {
            console.log('Full error:', err.response?.data)
            this.submitError = err.response?.data?.msg || 'Booking failed. Please try again.'
            } finally {
            this.isSubmitting = false
            }
        },

        handleCancel() {
            this.$emit('cancel')
        },
        async handleDelete() {
            if (!confirm('Are you sure you want to cancel this booking?')) return

            const token = localStorage.getItem('token')
            try {
                await axios.delete(`http://127.0.0.1:5000/bookings/${this.booking.booking_id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                this.$emit('deleted')  // tell parent to close modal + refresh list
            } catch (err) {
                this.submitError = err.response?.data?.msg || 'Could not cancel booking.'
            }
        },
        formatDate(iso) {
            if (!iso) return '—'
            return new Date(iso).toLocaleDateString('en-IN', {
                day: '2-digit', month: 'short', year: 'numeric'
            })
        },
    },
}
</script>

<style scoped>
/* Trek banner */
.trek-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #f3edff 0%, #e8f4fd 100%);
    border-left: 4px solid #9e52eb;
    border-radius: 8px;
    padding: 14px 18px;
    gap: 12px;
}
.trek-banner-name {
    font-weight: 700;
    font-size: 1.05rem;
    color: #2d2d2d;
}
.trek-banner-meta {
    font-size: 0.82rem;
    color: #666;
    margin-top: 4px;
}
.trek-banner-price {
    font-size: 1.4rem;
    font-weight: 800;
    color: #9e52eb;
    white-space: nowrap;
}
.trek-banner-price span {
    font-size: 0.75rem;
    font-weight: 500;
    color: #888;
}

/* Empty state */
.empty-participants {
    background: #fafafa;
    border: 1.5px dashed #ccc;
    border-radius: 8px;
    text-align: center;
    padding: 18px;
    color: #888;
    font-size: 0.9rem;
}

/* Participant card */
.participant-card {
    background: #fff;
    border: 1px solid #e4d9f9;
    border-radius: 10px;
    padding: 14px 16px 10px;
}
.participant-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9e52eb;
}
.btn-remove {
    background: none;
    border: none;
    color: #dc3545;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
}
.btn-remove:hover { color: #a71d2a; }

.field-error {
    color: #dc3545;
    font-size: 0.75rem;
    margin-top: 3px;
}

/* Cost summary */
.cost-summary {
    background: #f8f5ff;
    border-radius: 8px;
    padding: 10px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.95rem;
    color: #555;
}
.cost-total {
    font-size: 1.15rem;
    font-weight: 800;
    color: #9e52eb;
}

/* Disable opacity fix (matches Trek.vue) */
.btn-primary, .btn-secondary, .btn-success {
    opacity: 1 !important;
}
</style>