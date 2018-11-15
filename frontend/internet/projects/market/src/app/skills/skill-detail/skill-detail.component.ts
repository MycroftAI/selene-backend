import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, ParamMap } from '@angular/router';
import { Observable } from 'rxjs/internal/Observable';
import { switchMap, tap } from 'rxjs/operators';

import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';

import { InstallService } from '../install.service';
import { SkillDetail, SkillsService } from '../skills.service';

@Component({
  selector: 'market-skill-detail',
  templateUrl: './skill-detail.component.html',
  styleUrls: ['./skill-detail.component.scss']
})
export class SkillDetailComponent implements OnInit {
    public backArrow = faArrowLeft;
    public skill$: Observable<SkillDetail>;

    constructor(
        private installService: InstallService,
        private route: ActivatedRoute,
        private router: Router,
        private skillsService: SkillsService
    ) { }


    ngOnInit() {
        this.installService.getSkillInstallations();
        this.skill$ = this.route.paramMap.pipe(
            switchMap(
                (params: ParamMap) => this.skillsService.getSkillById(params.get('skillName'))
            ),
            tap(
                () => { this.installService.getSkillInstallations(); }
            )
        );
    }
}
