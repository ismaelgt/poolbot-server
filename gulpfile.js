var gulp = require('gulp');
var babel = require('gulp-babel');

gulp.task("babel", function(){
    return gulp.src("src/leaderboard/static/js/*.jsx").
        pipe(babel({
            plugins: ['transform-react-jsx']
        })).
        pipe(gulp.dest("src/leaderboard/static/js/"));
});

gulp.task('default', ['babel']);
