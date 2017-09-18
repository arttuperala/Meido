let cleanCSS = require('gulp-clean-css');
var gulp = require('gulp');
var sass = require('gulp-sass');


gulp.task('css', function() {
  return gulp.src('stylesheets/meido.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(cleanCSS())
    .pipe(gulp.dest('meido/static/css'))
});

gulp.task('watch', [
    'watch:css'
]);

gulp.task('watch:css', function () {
    gulp.watch('./stylesheets/**/*.scss', ['css']);
});

gulp.task('default', [
    'css',
]);
