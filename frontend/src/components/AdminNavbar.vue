<template>

<nav class="navbar navbar-light bg-light fixed-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Admin Dashboard</a>
    <div class="d-flex gap-2">
      <button class="btn btn-sm btn-danger" @click="signOut">Sign Out</button>
      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvaslightNavbar" aria-controls="offcanvaslightNavbar" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
    </div>
    <div class="offcanvas offcanvas-end text-bg-light" tabindex="-1" id="offcanvaslightNavbar" aria-labelledby="offcanvaslightNavbarLabel">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="offcanvaslightNavbarLabel">Admin Menu</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <ul class="navbar-nav flex-column">
          <li class="nav-item mb-2">
            <a class="nav-link active" aria-current="page" @click="() => $router.push('/admin')">Dashboard</a>
          </li>
          <li class="nav-item mb-2">
            <a class="nav-link" @click="() => $router.push('/admin/treks')">Treks</a>
          </li>
          <li class="nav-item mb-2">
            <a class="nav-link" href="#staff">Staff</a>
          </li>
          <li class="nav-item mb-2">
            <a class="nav-link" @click="() => $router.push('/admin/bookings')">Bookings</a>
          </li>
          <li class="nav-item mb-2">
            <a class="nav-link" href="#users">Users</a>
          </li>
          <li class="nav-item mb-2">
            <a class="nav-link" href="#stats">Stats</a>
          </li>
        </ul>
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