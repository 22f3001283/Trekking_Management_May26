<template>
  <div>
    <StaffNavbar />

    <div class="container" style="padding-top: 90px; padding-bottom: 60px;">

      <!-- Back link -->
      <button v-if="backPath" class="btn btn-light mb-3" type="button" @click="$router.push(backPath)">
        <i class="bi bi-arrow-left"></i>  Back to dashboard
      </button>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="loadError" class="alert alert-danger mt-4" role="alert">
        {{ loadError }}
      </div>

      <!-- Profile layout -->
      <div v-else class="mx-auto" style="max-width: 880px;">
        <div class="d-flex flex-column flex-md-row gap-4 align-items-center align-items-md-start">

          <!-- Left: avatar -->
          <div class="d-flex justify-content-center flex-shrink-0" style="width: 100%; max-width: 200px;">
            <div class="rounded-5 d-flex align-items-center justify-content-center fw-semibold text-white"
                 style="width: 88px; height: 88px; font-size: 1.4rem; background-color:#4877d4; color: white">
              {{ initials }}
            </div>
          </div>

          <!-- Right: details panel -->
          <div class="rounded-3 p-4 flex-grow-1 w-100" style="background-color: #f3f4f6; max-width: 600px;">

            <div class="d-flex flex-column flex-sm-row align-items-sm-center mb-3">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Username</label>
              <input type="text" class="form-control w-100" style="max-width: 380px;" :value="profile.username" disabled>
            </div>

            <div class="d-flex flex-column flex-sm-row align-items-sm-center mb-3">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Email</label>
              <input type="text" class="form-control w-100" style="max-width: 380px;" :value="profile.email" disabled>
            </div>

            <div class="d-flex flex-column flex-sm-row align-items-sm-center mb-3">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Contact</label>
              <input type="text" class="form-control w-100" style="max-width: 380px;" :value="profile.contact || '—'" disabled>
            </div>

            <div class="d-flex flex-column flex-sm-row align-items-sm-center mb-3">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Role</label>
              <input type="text" class="form-control text-capitalize w-100" style="max-width: 380px;" :value="profile.role" disabled>
            </div>

            <div class="d-flex flex-column flex-sm-row align-items-sm-center mb-3">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Status</label>
              <input type="text" class="form-control text-capitalize fw-semibold w-100" :class="statusClass"
                     style="max-width: 380px;" :value="profile.status" disabled>
            </div>

            <div v-if="profile.created_at" class="d-flex flex-column flex-sm-row align-items-sm-center">
              <label class="text-secondary mb-1 mb-sm-0" style="width: 160px; min-width: 140px;">Member Since</label>
              <input type="text" class="form-control w-100" style="max-width: 380px;" :value="formattedDate" disabled>
            </div>

          </div>
        </div>

        <!-- Edit Profile button — end of the page -->
        <div class="d-flex justify-content-center justify-content-sm-end mt-4">
          <button class="btn btn-primary px-4" @click="openEditModal">
            Edit Profile
          </button>
        </div>
      </div>

    </div>

    <!-- Edit Profile Modal -->
    <div
      class="modal fade"
      id="editProfileModal"
      tabindex="-1"
      aria-labelledby="editProfileModalLabel"
      aria-hidden="true"
      ref="editModalEl"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editProfileModalLabel">Edit Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <form @submit.prevent="submitEdit">
            <div class="modal-body">

              <div v-if="editError" class="alert alert-danger py-2">{{ editError }}</div>
              <div v-if="editSuccess" class="alert alert-success py-2">{{ editSuccess }}</div>

              <div class="mb-3">
                <label class="form-label">Username</label>
                <input
                  type="text"
                  class="form-control"
                  v-model.trim="form.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  v-model.trim="form.email"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact</label>
                <input
                  type="text"
                  class="form-control"
                  v-model.trim="form.contact"
                  placeholder="Phone number"
                />
              </div>

              <hr class="my-3" />
              <p class="text-muted small mb-2">Leave password fields blank to keep your current password.</p>

              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <div class="input-group">
                  <input
                    :type="showCurrentPassword ? 'text' : 'password'"
                    class="form-control"
                    v-model="form.current_password"
                    autocomplete="current-password"
                  />
                  <button
                    type="button"
                    class="input-group-text bg-white text-muted"
                    @click="showCurrentPassword = !showCurrentPassword"
                    :aria-label="showCurrentPassword ? 'Hide password' : 'Show password'"
                  >
                    <svg v-if="!showCurrentPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.6 21.6 0 0 1 5.06-5.94M9.9 4.24A10.6 10.6 0 0 1 12 4c7 0 11 7 11 7a21.6 21.6 0 0 1-2.16 3.19" />
                      <path d="M14.12 14.12A3 3 0 1 1 9.88 9.88" />
                      <path d="M1 1l22 22" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <div class="input-group">
                  <input
                    :type="showNewPassword ? 'text' : 'password'"
                    class="form-control"
                    :class="{ 'is-invalid': passwordError }"
                    v-model="form.new_password"
                    autocomplete="new-password"
                    @input="validateNewPassword"
                  />
                  <button
                    type="button"
                    class="input-group-text bg-white text-muted"
                    @click="showNewPassword = !showNewPassword"
                    :aria-label="showNewPassword ? 'Hide password' : 'Show password'"
                  >
                    <svg v-if="!showNewPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.6 21.6 0 0 1 5.06-5.94M9.9 4.24A10.6 10.6 0 0 1 12 4c7 0 11 7 11 7a21.6 21.6 0 0 1-2.16 3.19" />
                      <path d="M14.12 14.12A3 3 0 1 1 9.88 9.88" />
                      <path d="M1 1l22 22" />
                    </svg>
                  </button>
                </div>
                <div v-if="passwordError" class="text-danger small mt-1">{{ passwordError }}</div>
              </div>

            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                Save Changes
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
import StaffNavbar from '../../components/StaffNavbar.vue'

export default {
  name: 'StaffProfile',
  components: { StaffNavbar },
  data() {
    return {
      profile: {},
      loading: true,
      loadError: '',
      saving: false,
      editError: '',
      editSuccess: '',
      passwordError: '',
      showCurrentPassword: false,
      showNewPassword: false,
      modalInstance: null,
      form: {
        username: '',
        email: '',
        contact: '',
        current_password: '',
        new_password: ''
      }
    }
  },
  computed: {
    initials() {
      if (!this.profile.username) return '?'
      return this.profile.username.slice(0, 2).toUpperCase()
    },
    statusClass() {
      const s = (this.profile.status || '').toLowerCase()
      if (s === 'active') return 'text-success'
      if (s === 'blacklisted') return 'text-danger'
      return 'text-body'
    },
    passwordRegex() {
      return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,20}$/
    },
    formattedDate() {
      if (!this.profile.created_at) return ''
      const d = new Date(this.profile.created_at)
      if (isNaN(d)) return this.profile.created_at
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },
    backPath() {
      const userId = localStorage.getItem('user_id')
      return userId ? `/staff/${userId}` : null
    }
  },
  mounted() {
    this.fetchProfile()
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem('token')
      return { Authorization: `Bearer ${token}` }
    },
    async fetchProfile() {
      this.loading = true
      this.loadError = ''
      try {
        const res = await axios.get('http://127.0.0.1:5000/staff/profile', { headers: this.authHeaders() })
        this.profile = res.data
      } catch (err) {
        this.loadError =
          err.response?.data?.msg || 'Could not load your profile. Please try again.'
      } finally {
        this.loading = false
      }
    },
    openEditModal() {
      this.editError = ''
      this.editSuccess = ''
      this.passwordError = ''
      this.showCurrentPassword = false
      this.showNewPassword = false
      this.form = {
        username: this.profile.username || '',
        email: this.profile.email || '',
        contact: this.profile.contact || '',
        current_password: '',
        new_password: ''
      }
      this.modalInstance = bootstrap.Modal.getOrCreateInstance(this.$refs.editModalEl)
      this.modalInstance.show()
    },
    validateNewPassword() {
      if (!this.form.new_password) {
        this.passwordError = ''
        return true // blank is fine — means "keep current password"
      }
      if (this.form.new_password.length < 8 || this.form.new_password.length > 20) {
        this.passwordError = 'Password must be 8–20 characters long'
        return false
      }
      if (!this.passwordRegex.test(this.form.new_password)) {
        this.passwordError = 'Must include uppercase, lowercase, a digit, and a special character'
        return false
      }
      this.passwordError = ''
      return true
    },
    async submitEdit() {
      this.editError = ''
      this.editSuccess = ''

      if (this.form.new_password && !this.form.current_password) {
        this.editError = 'Enter your current password to set a new one.'
        return
      }

      if (!this.validateNewPassword()) {
        return
      }

      this.saving = true
      try {
        const payload = {
          username: this.form.username,
          email: this.form.email,
          contact: this.form.contact
        }
        if (this.form.new_password) {
          payload.current_password = this.form.current_password
          payload.new_password = this.form.new_password
        }

        const res = await axios.put('http://127.0.0.1:5000/staff/profile', payload, { headers: this.authHeaders() })
        this.profile = res.data.user || { ...this.profile, ...payload }
        this.editSuccess = res.data.msg || 'Profile updated successfully'

        // brief pause so the user sees the success message, then close
        setTimeout(() => {
          this.modalInstance.hide()
          this.editSuccess = ''
        }, 900)
      } catch (err) {
        this.editError = err.response?.data?.msg || 'Could not update profile. Please try again.'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>