import update_games as update_games
import update_books as update_books

update_books.fetch_book_covers()
update_games.fetch_game_covers()
update_games.generate_games_data_yaml()