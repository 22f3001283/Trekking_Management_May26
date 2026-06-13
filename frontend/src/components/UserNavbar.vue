<template>
  <nav class="navbar navbar-light bg-light fixed-top">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">Dashboard</a>
      <div class="d-flex gap-3 align-items-center">
        <div class="icon-wrap">
          <button class="icon-btn">
            <img src="../assets/history.png" alt="History" class="nav-icon" />
          </button>
          <span class="tooltip-label">History</span>
        </div>
        <div class="icon-wrap">
          <button class="icon-btn">
            <img src="../assets/profile.png" alt="Profile" class="nav-icon" />
          </button>
          <span class="tooltip-label">Profile</span>
        </div>
        <div class="icon-wrap">
          <button class="icon-btn" @click="signOut">
            <img src="../assets/signout.png" alt="Sign Out" class="nav-icon" />
          </button>
          <span class="tooltip-label">Sign Out</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  methods: {
    signOut() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease;
}

.icon-btn:hover {
  background-color: rgba(0, 0, 0, 0.08);
}

.icon-btn:active {
  background-color: rgba(0, 0, 0, 0.14);
}

.nav-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.tooltip-label {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
  z-index: 9999;
}

.tooltip-label::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-bottom-color: #333;
}

.icon-wrap:hover .tooltip-label {
  opacity: 1;
}
</style>