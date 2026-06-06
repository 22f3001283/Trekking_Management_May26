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

		<footer class="footer">© 2026 Trekking Management. All rights reserved.</footer>
	</div>
</template>

<script>
import homeImg from "../assets/homePage.jpg"
</script>