import { Component, Input } from '@angular/core';
import { SkillDetail } from '../../skills.service';
import { faCodeBranch } from '@fortawesome/free-solid-svg-icons';

@Component({
    selector: 'market-skill-detail-header',
    templateUrl: './skill-detail-header.component.html',
    styleUrls: ['./skill-detail-header.component.scss']
})
export class SkillDetailHeaderComponent {
    public githubIcon = faCodeBranch;
    @Input() public skill: SkillDetail;

    constructor() { }

    navigateToGithubRepo(githubRepoUrl) {
        window.open(githubRepoUrl);
    }
}
