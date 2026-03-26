# TODO List for Django Event Management Project Fixes

## Completed Tasks
- [x] Fix tbl_register model: Change phone to CharField, add OneToOneField to User.
- [x] Update register view to properly link User and tbl_register, add OTP sending.
- [x] Implement verify_otp view function to handle OTP verification.
- [x] Implement resend_otp view function to resend OTP.
- [x] Update verify_otp.html template with consistent styling and messages.

## Pending Tasks
- [ ] Run makemigrations and migrate to apply model changes.
- [ ] Test the registration process with OTP verification.
- [ ] Ensure consistent user handling across views (use User objects instead of usernames where possible).
- [ ] Test the server to check for any remaining errors.
