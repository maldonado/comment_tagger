from django.shortcuts import render
from django.db.models import Count

from .models import Repositories
from .models import ProcessedComments

# Create your views here.
def home(request):
	
	repositories = Repositories.objects.all().order_by('-cloned_date')[:5]
	
	context = { 
		"recent_repositories": repositories
	}
	
	return render(request, "home.html", context)


def repo(request, repo_id):

	current_comments = ProcessedComments.objects.all().filter(repository_id=repo_id, td_classification='DESIGN', is_introduced_version=True)
	
	#had_td = current_comments.filter(has_removed_version=True).distinct('file_id')	
	#has_td = current_comments.filter(has_removed_version=False).distinct('file_id')	
	#had_td = current_comments.filter(has_removed_version=True)	
	#print(len(had_td))
	#print(len(has_td))
	

	context = { 
		"processed_comments": current_comments
	}

	return render(request, "repo.html", context)