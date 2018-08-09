import { Component, EventEmitter, OnInit, Output } from '@angular/core';

import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';

import { SkillsService } from "../skills.service";

@Component({
    selector: 'market-skill-toolbar',
    templateUrl: './skill-toolbar.component.html',
    styleUrls: ['./skill-toolbar.component.scss']
})
export class SkillToolbarComponent implements OnInit {
    public languages = [
        {value: 'english', display: 'English'}
    ];
    public searchIcon = faSearch;
    @Output() public searchResults = new EventEmitter();
    public searchTerm: string;
    public selectedLanguage = this.languages[0].value;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() { }

    onClick(): void {
        if (this.searchIcon === faSearch) {
            this.searchSkills();
            this.searchIcon = faTimes;
        } else {
            this.searchTerm = '';
            this.searchSkills();
            this.searchIcon = faSearch;
        }
    }

    searchSkills(): void {
        this.skillsService.searchSkills(this.searchTerm).subscribe(
            (skills) => {
                this.searchResults.emit(skills);
            }
        );
    }
}
